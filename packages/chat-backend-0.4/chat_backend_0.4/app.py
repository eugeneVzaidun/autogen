from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
import asyncio


# Define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."


async def main() -> None:
    # Define an agent
    assistant = AssistantAgent(
        name="assistant",
        model_client=OpenAIChatCompletionClient(model="gpt-4o-2024-08-06"),
        tools=[get_weather],
    )

    # Define termination condition
    termination = MaxMessageTermination(5) | TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([assistant], termination_condition=termination)

    # Run the team and stream messages
    # await agent_team.reset()

    task2 = await agent_team.run(task="What is the weather in New York?")
    print(task2.messages)

    # task1 = await agent_team.run(task="What was my last question?")
    # print(task1.messages)


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
asyncio.run(main())
