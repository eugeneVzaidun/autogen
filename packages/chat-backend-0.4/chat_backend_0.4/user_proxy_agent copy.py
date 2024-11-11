import asyncio
from typing import List, Sequence

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import (
    ChatMessage,
    StopMessage,
    TextMessage,
)
from autogen_core.base import CancellationToken


class UserProxyAgent(BaseChatAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name, "A human user.")

    @property
    def produced_message_types(self) -> List[type[ChatMessage]]:
        return [TextMessage, StopMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        # Process incoming messages from AssistantAgent
        for message in messages:
            if isinstance(message, TextMessage):
                print(f"Assistant: {message.content}")
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter your response: ")
        if "TERMINATE" in user_input:
            return Response(chat_message=StopMessage(content="User has terminated the conversation.", source=self.name))
        return Response(chat_message=TextMessage(content=user_input, source=self.name))

    async def reset(self, cancellation_token: CancellationToken) -> None:
        pass

    def on_reset(self, cancellation_token):
        return super().on_reset(cancellation_token)


# user_proxy_agent = UserProxyAgent(name="user_proxy_agent")


# async def main():
#     user_proxy_agent = UserProxyAgent(name="user_proxy_agent")

#     user_proxy_agent_result = await user_proxy_agent.on_messages(
#         messages=[
#             TextMessage(content="What is the weather right now in France?", source="user"),
#         ],
#         cancellation_token=CancellationToken(),
#     )
#     print(user_proxy_agent_result)


# asyncio.run(main())
