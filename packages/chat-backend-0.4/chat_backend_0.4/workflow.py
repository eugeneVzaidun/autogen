import tools
from fastapi import WebSocket
from autogen_ext.models import OpenAIChatCompletionClient
from autogen_core import SingleThreadedAgentRuntime, TypeSubscription
from agents import AIAgent, HumanAgent, WebSocketUserAgent
import prompts

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")


async def initialize_agents(runtime: SingleThreadedAgentRuntime, session_id: str, websocket: WebSocket):
    # Register the general agent
    general_agent_type = await AIAgent.register(
        runtime,
        type=tools.general_agent_topic_type,
        factory=lambda: AIAgent(
            description=prompts.GENERAL_AGENT_DESCRIPTION,
            system_message=prompts.GENERAL_AGENT_SYSTEM_MESSAGE,
            model_client=model_client,
            tools=[tools.execute_task_tool, tools.lookup_resource_tool],
            delegate_tools=[tools.delegate_to_support_agent_tool, tools.escalate_to_human_agent_tool],
            agent_topic_type=tools.general_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.general_agent_topic_type, agent_type=general_agent_type.type)
    )

    # Register the support agent
    support_agent_type = await AIAgent.register(
        runtime,
        type=tools.support_agent_topic_type,
        factory=lambda: AIAgent(
            description=prompts.SUPPORT_AGENT_DESCRIPTION,
            system_message=prompts.SUPPORT_AGENT_SYSTEM_MESSAGE,
            model_client=model_client,
            tools=[tools.process_refund_tool],
            delegate_tools=[tools.delegate_back_to_escalation_tool],
            agent_topic_type=tools.support_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.support_agent_topic_type, agent_type=support_agent_type.type)
    )

    # Register the human agent
    human_agent_type = await HumanAgent.register(
        runtime,
        type=tools.human_agent_topic_type,
        factory=lambda: HumanAgent(
            description=prompts.HUMAN_AGENT_DESCRIPTION,
            agent_topic_type=tools.human_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.human_agent_topic_type, agent_type=human_agent_type.type)
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
