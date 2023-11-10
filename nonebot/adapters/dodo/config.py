from typing import List

from pydantic import BaseModel, Extra, Field


class BotConfig(BaseModel, extra=Extra.ignore):
    client_id: str
    token: str


class Config(BaseModel, extra=Extra.ignore):
    bots: List[BotConfig] = Field(default_factory=list, alias="dodo_bots")
