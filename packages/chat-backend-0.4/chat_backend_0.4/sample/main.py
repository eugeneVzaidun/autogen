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

    # Register the triage agent.
    triage_agent_type = await AIAgent.register(
        runtime,
        type=tools.triage_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A triage agent.",
            system_message=SystemMessage(
                content="You are a customer service bot for ACME Inc. "
                "Introduce yourself. Always be very brief. "
                "Gather information to direct the customer to the right department. "
                "But make your questions subtle and natural."
            ),
            model_client=model_client,
            tools=[],
            delegate_tools=[
                tools.transfer_to_sales_agent_tool,
                tools.escalate_to_human_tool,
            ],
            agent_topic_type=tools.triage_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    # Add subscriptions for the triage agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.triage_agent_topic_type, agent_type=triage_agent_type.type)
    )

    # Register the sales agent.
    sales_agent_type = await AIAgent.register(
        runtime,
        type=tools.sales_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A sales agent.",
            system_message=SystemMessage(
                content="You are a sales agent for ACME Inc."
                "Always answer in a sentence or less."
                "Follow the following routine with the user:"
                "1. Ask them about any problems in their life related to catching roadrunners.\n"
                "2. Casually mention one of ACME's crazy made-up products can help.\n"
                " - Don't mention price.\n"
                "3. Once the user is bought in, drop a ridiculous price.\n"
                "4. Only after everything, and if the user says yes, "
                "tell them a crazy caveat and execute their order.\n"
                ""
            ),
            model_client=model_client,
            tools=[tools.execute_order_tool],
            delegate_tools=[tools.transfer_back_to_triage_tool],
            agent_topic_type=tools.sales_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.sales_agent_topic_type, agent_type=sales_agent_type.type)
    )

    # Register the human agent.
    human_agent_type = await HumanAgent.register(
        runtime,
        type=tools.human_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: HumanAgent(
            description="A human agent.",
            agent_topic_type=tools.human_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    # Add subscriptions for the human agent: it will receive messages published to its own topic only.
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
            agent_topic_type=tools.triage_agent_topic_type,  # Start with the triage agent.
        ),
    )
    # Add subscriptions for the user agent: it will receive messages published to its own topic only.
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
