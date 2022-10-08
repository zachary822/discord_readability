from pathlib import Path

import pyphen
from spacy import Language
from spacy.tokens import Doc, Token


@Language.factory(
    "readability",
    assigns=["doc._.flesch_kincaid_grade"],
)
def make_spacy_readability(nlp: Language, name: str):
    return SpacyReadability(nlp, name)


class SpacyReadability:
    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        self.name = name

        self.syllable_dic = pyphen.Pyphen(lang="en_US")

        Doc.set_extension("flesch_kincaid_grade", default=None, force=True)
        Token.set_extension("syllables_count", default=None, force=True)

    def __call__(self, doc: Doc):
        num_sentences = len(list(doc.sents))
        num_words = sum(1 for t in doc if not t.is_punct)
        num_syllables = sum(c for t in doc if (c := t._.syllables_count))
        try:
            grade = (
                (11.8 * num_syllables / num_words)
                + (0.39 * num_words / num_sentences)
                - 15.59
            )
            doc._.set("flesch_kincaid_grade", grade)
        except ZeroDivisionError:
            pass

        return doc


@Language.factory(
    "syllables",
    assigns=["token._.syllables", "token._.syllables_count"],
    requires=["token.text"],
)
def make_spacysyllables(nlp: Language, name: str):
    return SpacySyllables(nlp, name)


class SpacySyllables:
    cmudict: dict[str, int] = {}

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        self.name = name
        self.syllable_dic = pyphen.Pyphen(lang="en_US")
        self.load_cmudict()

        Token.set_extension("syllables_count", default=None, force=True)

    @classmethod
    def load_cmudict(cls):
        with (Path(__file__).resolve().parent / "cmudict-0.7b.txt").open("r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(";;;"):
                    continue
                word, _, pronunciation = line.partition(" ")
                cls.cmudict[word.casefold()] = sum(c.isdigit() for c in pronunciation)

    def syllables(self, word: str):
        try:
            return self.cmudict[word]
        except KeyError:
            return self.syllable_dic.inserted(word.casefold()).count("-") + 1

    def __call__(self, doc: Doc):
        for token in doc:
            token._.set("syllables_count", self.syllables(token.text.casefold()))
        return doc
