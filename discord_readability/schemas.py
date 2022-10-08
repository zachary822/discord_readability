from pydantic import BaseModel


class Message(BaseModel):
    content: str


class ResolvedData(BaseModel):
    messages: dict[str, Message]


class InteractionData(BaseModel):
    id: str
    name: str
    resolved: ResolvedData
    target_id: str
    type: int


class Interaction(BaseModel):
    application_id: str
    channel_id: str
    data: InteractionData
    token: str
    type: int
