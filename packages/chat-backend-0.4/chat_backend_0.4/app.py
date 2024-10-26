import logging
import asyncio
from autogen_agentchat import EVENT_LOGGER_NAME
from autogen_agentchat.agents import ToolUseAssistantAgent
from autogen_agentchat.logging import ConsoleLogHandler
from autogen_agentchat.teams import MaxMessageTermination, RoundRobinGroupChat
from autogen_core.components.tools import FunctionTool
from autogen_ext.models import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(ConsoleLogHandler())
logger.setLevel(logging.INFO)


# define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."


# wrap the tool for use with the agent
get_weather_tool = FunctionTool(get_weather, description="Get the weather for a city")

# define an agent
weather_agent = ToolUseAssistantAgent(
    name="writing_agent",
    model_client=OpenAIChatCompletionClient(model="gpt-4o-2024-08-06"),
    registered_tools=[get_weather_tool],
)

# add the agent to a team
agent_team = RoundRobinGroupChat([weather_agent])


# Note: if running in a Python file directly you'll need to use asyncio.run(agent_team.run(...)) instead of await agent_team.run(...)
async def main():
    result = await agent_team.run(
        task="What is the weather in New York?",
        termination_condition=MaxMessageTermination(max_messages=1),
    )
    print("\n", result)


asyncio.run(main())
