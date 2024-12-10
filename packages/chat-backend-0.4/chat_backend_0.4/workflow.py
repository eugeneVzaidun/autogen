import tools
from fastapi import WebSocket
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import SingleThreadedAgentRuntime, TypeSubscription
from agents import AIAgent, HumanAgent, WebSocketUserAgent
import prompts

model_client = OpenAIChatCompletionClient(model="gpt-4o")


async def initialize_agents(runtime: SingleThreadedAgentRuntime, session_id: str, websocket: WebSocket):
    # Register the general agent
    general_agent_type = await AIAgent.register(
        runtime,
        type=tools.general_agent_topic_type,
        factory=lambda: AIAgent(
            description=prompts.GENERAL_AGENT_DESCRIPTION,
            system_message=prompts.GENERAL_AGENT_SYSTEM_MESSAGE,
            model_client=model_client,
            tools=[],
            delegate_tools=[],
            agent_topic_type=tools.general_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.general_agent_topic_type, agent_type=general_agent_type.type)
    )

    # Register the user agent using the WebSocketUserAgent
    user_agent_type = await WebSocketUserAgent.register(
        runtime,
        type=tools.user_topic_type,
        factory=lambda: WebSocketUserAgent(
            description=prompts.USER_AGENT_DESCRIPTION,
            user_topic_type=tools.user_topic_type,
            agent_topic_type=tools.general_agent_topic_type,
            websocket=websocket,
        ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=tools.user_topic_type, agent_type=user_agent_type.type))
