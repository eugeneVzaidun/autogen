import asyncio
import uuid

from autogen_core import (
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
)
from autogen_core.components.models import (
    SystemMessage,
)
from autogen_ext.models import OpenAIChatCompletionClient

from models import UserLogin
from agents import AIAgent, HumanAgent, UserAgent
import tools


async def main():
    runtime = SingleThreadedAgentRuntime()

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
    )

    # Register the general agent.
    general_agent_type = await AIAgent.register(
        runtime,
        type=tools.general_agent_topic_type,  # Using the generic topic type.
        factory=lambda: AIAgent(
            description="A general-purpose agent.",
            system_message=SystemMessage(
                content="You are a versatile agent capable of handling various business workflows. "
                "Assist users by performing tasks, retrieving information, and escalating issues when necessary."
            ),
            model_client=model_client,
            tools=[tools.execute_task_tool, tools.lookup_resource_tool],
            delegate_tools=[
                tools.delegate_to_support_agent_tool,
                tools.escalate_to_human_agent_tool,
            ],
            agent_topic_type=tools.general_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    # Add subscriptions for the general agent.
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.general_agent_topic_type, agent_type=general_agent_type.type)
    )

    # Register the support agent.
    support_agent_type = await AIAgent.register(
        runtime,
        type=tools.support_agent_topic_type,  # Define a new support agent topic type.
        factory=lambda: AIAgent(
            description="A support agent.",
            system_message=SystemMessage(
                content="You are a support agent specialized in assisting with customer inquiries and issues."
            ),
            model_client=model_client,
            tools=[tools.process_refund_tool],
            delegate_tools=[tools.delegate_back_to_escalation_tool],
            agent_topic_type=tools.support_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    # Add subscriptions for the support agent.
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.support_agent_topic_type, agent_type=support_agent_type.type)
    )

    # Register the human agent.
    human_agent_type = await HumanAgent.register(
        runtime,
        type=tools.human_agent_topic_type,  # Using the generic human agent topic type.
        factory=lambda: HumanAgent(
            description="A human agent.",
            agent_topic_type=tools.human_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    # Add subscriptions for the human agent.
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.human_agent_topic_type, agent_type=human_agent_type.type)
    )

    # Register the user agent.
    user_agent_type = await UserAgent.register(
        runtime,
        type=tools.user_topic_type,
        factory=lambda: UserAgent(
            description="A user agent.",
            user_topic_type=tools.user_topic_type,
            agent_topic_type=tools.general_agent_topic_type,  # Start with the general agent.
        ),
    )
    # Add subscriptions for the user agent.
    await runtime.add_subscription(TypeSubscription(topic_type=tools.user_topic_type, agent_type=user_agent_type.type))

    # Start the runtime.
    runtime.start()

    # Create a new session for the user.
    session_id = str(uuid.uuid4())
    await runtime.publish_message(UserLogin(), topic_id=TopicId(tools.user_topic_type, source=session_id))

    # Run until completion.
    await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())
