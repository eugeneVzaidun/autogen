import asyncio
from typing import List, Sequence
import logging

from fastapi.websockets import WebSocketState

from fastapi import WebSocket, WebSocketDisconnect

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import (
    ChatMessage,
    StopMessage,
    TextMessage,
    FunctionExecutionResult,  # Added FunctionExecutionResult
)
from autogen_core.base import CancellationToken

# Configure logging
logging.basicConfig(level=logging.INFO)


class UserProxyAgent(BaseChatAgent):
    def __init__(self, name: str, websocket: WebSocket) -> None:
        super().__init__(name, "A human user.")
        self.websocket = websocket

    @property
    def produced_message_types(self) -> List[type[ChatMessage]]:
        return [TextMessage, StopMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        # Process incoming messages from AssistantAgent
        print("!!!!!!!!!!!!!!!")
        print(messages)
        print("!!!!!!!!!!!!!!!")
        for message in messages:
            if isinstance(message, TextMessage):
                logging.info(f"Assistant: {message.content}")
                await self.websocket.send_text(f"Assistant: {message.content}")
            elif isinstance(message, FunctionExecutionResult):
                logging.info(f"Function result: {message.content}")
                await self.websocket.send_text(f"Function result: {message.content}")
        if self.websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                user_input = await self.websocket.receive_text()
                if "TERMINATE" in user_input:
                    logging.info("User has terminated the conversation.")
                    return Response(
                        chat_message=StopMessage(content="User has terminated the conversation.", source=self.name)
                    )
                logging.info(f"User response: {user_input}")
                return Response(chat_message=TextMessage(content=user_input, source=self.name))
            except WebSocketDisconnect:
                logging.warning("WebSocket disconnected while waiting for user input.")
                return Response(chat_message=StopMessage(content="WebSocket disconnected.", source=self.name))
        else:
            logging.warning("WebSocket is disconnected.")
            return Response(chat_message=StopMessage(content="WebSocket is disconnected.", source=self.name))

    async def reset(self, cancellation_token: CancellationToken) -> None:
        pass

    def on_reset(self, cancellation_token):
        return super().on_reset(cancellation_token)
