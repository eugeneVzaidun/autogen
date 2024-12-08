from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
import asyncio
from user_proxy_agent import UserProxyAgent


async def main() -> None:
    # Define an agent
    assistant = AssistantAgent(
        name="assistant",
        model_client=OpenAIChatCompletionClient(model="gpt-4o-2024-08-06"),
        # tools=[get_weather],
    )
    userProxyAssistant = UserProxyAgent(name="user_proxy_agent")
    # Define termination condition
    termination = TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([assistant, userProxyAssistant], termination_condition=termination)

    # Run the team
    print(await agent_team.run(task="Greatings! How can I help you today?"))


asyncio.run(main())
