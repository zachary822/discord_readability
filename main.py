import json
import logging.config
from pathlib import Path

import requests
import spacy

import spacy_readability  # noqa
from discord_readability.schemas import Interaction

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("syllables", after="tagger")
nlp.add_pipe("readability", after="parser")

with (Path(__file__).resolve().parent / "logging.conf").open("r") as f:
    logging.config.fileConfig(f)

logger = logging.getLogger(__name__)


def handler(event, context):
    if logger.isEnabledFor(logging.INFO):
        logger.info("Event: %s", json.dumps(event))

    interaction = Interaction(**event["detail"])

    message = interaction.data.resolved.messages[interaction.data.target_id]

    doc = nlp(message.content)

    with requests.Session() as session:
        resp = session.patch(
            f"https://discord.com/api/webhooks/{interaction.application_id}/{interaction.token}/messages/@original",
            json={
                "content": (
                    f"Flesch-Kincaid grade level: {doc._.flesch_kincaid_grade:.3}\n"
                    + f"original: https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{message.id}"  # noqa: E501
                ),
                "message_reference": {
                    "channel_id": interaction.channel_id,
                    "guild_id": interaction.guild_id,
                    "message_id": message.id,
                },
            },
        )
        logger.info("status: %s body: %s", resp.status_code, resp.text)

    return {
        "statusCode": 200,
        "body": "",
    }
