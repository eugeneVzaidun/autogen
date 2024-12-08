from pydantic import BaseModel
from typing import List
from autogen_core.components.models import LLMMessage


class UserLogin(BaseModel):
    pass


class UserTask(BaseModel):
    context: List[LLMMessage]


class AgentResponse(BaseModel):
    reply_to_topic_type: str
    context: List[LLMMessage]
