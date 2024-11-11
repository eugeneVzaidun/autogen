from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
import asyncio


async def main() -> None:
    # Define an agent
    assistant = AssistantAgent(
        name="assistant",
        model_client=OpenAIChatCompletionClient(model="gpt-4o-2024-08-06"),
        # tools=[get_weather],
    )
    # Define termination condition
    termination = TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([assistant], termination_condition=termination)

    # Run the team
    print(await agent_team.run(task="How are you doing?"))


asyncio.run(main())
