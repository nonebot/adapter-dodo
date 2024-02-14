from typing import List

from pydantic import BaseModel, Field


class BotConfig(BaseModel):
    client_id: str
    token: str


class Config(BaseModel):
    bots: List[BotConfig] = Field(default_factory=list, alias="dodo_bots")
