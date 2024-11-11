from autogen_agentchat.agents import AssistantAgent, BaseChatAgent
from typing import AsyncGenerator, List, Sequence
from autogen_agentchat.messages import AgentMessage, ChatMessage, TextMessage
from autogen_core.base import CancellationToken
from autogen_agentchat.base import Response
from autogen_agentchat.task import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
import asyncio


class UserProxyAgent(BaseChatAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name, "A human user.")

    @property
    def produced_message_types(self) -> List[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter your response: ")
        return Response(chat_message=TextMessage(content=user_input, source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass


# Define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."


async def run_user_proxy_agent() -> None:
    user_proxy_agent = UserProxyAgent(name="user_proxy_agent")
    response = await user_proxy_agent.on_messages([], CancellationToken())
    print(response.chat_message)


async def main() -> None:
    # Define an agent
    assistant = AssistantAgent(
        name="assistant",
        model_client=OpenAIChatCompletionClient(model="gpt-4o-2024-08-06"),
        tools=[get_weather],
    )
    userProxy = UserProxyAgent(name="user_proxy_agent")
    # Define termination condition
    termination = MaxMessageTermination(5) | TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([userProxy, assistant], termination_condition=termination)

    # Run the team and stream messages
    # await agent_team.reset()

    task2 = await agent_team.run(task="What is the weather in New York?")
    print(task2.messages)

    # task1 = await agent_team.run(task="What was my last question?")
    # print(task1.messages)


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
asyncio.run(main())
# asyncio.run(run_user_proxy_agent())
