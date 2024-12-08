import asyncio
from typing import List, Sequence
import logging

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import (
    ChatMessage,
    StopMessage,
    TextMessage,
    AgentMessage,
    FunctionExecutionResult,  # Added FunctionExecutionResult
)
from autogen_core.base import CancellationToken

# Configure logging
logging.basicConfig(level=logging.INFO)


class UserProxyAgent(BaseChatAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name, "A human user.")

    @property
    def produced_message_types(self) -> List[type[ChatMessage]]:
        return [AgentMessage | ChatMessage | FunctionExecutionResult]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        # Process incoming messages from AssistantAgent
        for message in messages:
            if isinstance(message, TextMessage):
                logging.info(f"Assistant: {message.content}")
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter your response: ")
        if "TERMINATE" in user_input:
            logging.info("User has terminated the conversation.")
            return Response(chat_message=StopMessage(content="User has terminated the conversation.", source=self.name))
        logging.info(f"User response: {user_input}")
        return Response(chat_message=TextMessage(content=user_input, source=self.name))

    async def reset(self, cancellation_token: CancellationToken) -> None:
        pass

    def on_reset(self, cancellation_token):
        return super().on_reset(cancellation_token)
