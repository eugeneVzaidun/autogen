import asyncio
import uuid
import traceback
from dataclasses import dataclass

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from autogen_core import (
    SingleThreadedAgentRuntime,
    AgentId,
    MessageContext,
    message_handler,
    RoutedAgent,
    TopicId,
    TypeSubscription,
)

from autogen_core.components.models import (
    SystemMessage,
    UserMessage,
)
from autogen_ext.models import OpenAIChatCompletionClient

# Import your custom messages, agents, and tools
# Assuming these are from your code references:
from models import UserLogin, UserTask, AgentResponse
from agents import AIAgent, HumanAgent, UserAgent
import tools


@dataclass
class TextMessage:
    content: str
    source: str


model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")


# Modify UserAgent to send responses back to the user via WebSocket
class WebSocketUserAgent(UserAgent):
    def __init__(self, description: str, user_topic_type: str, agent_topic_type: str, websocket: WebSocket) -> None:
        super().__init__(description, user_topic_type, agent_topic_type)
        self.websocket = websocket

    @message_handler
    async def handle_user_login(self, message: UserLogin, ctx: MessageContext) -> None:
        # Notify the user that they have logged in
        await self.websocket.send_text("You have successfully logged in. You can now send your requests.")
        # No `input()` here. We simply wait for the user to send messages via websocket.

    @message_handler
    async def handle_task_result(self, message: AgentResponse, ctx: MessageContext) -> None:
        # The AgentResponse contains context. The last message in the context
        # is typically the agent's response to the user's query.
        # We'll send that back to the user via WebSocket.
        # Extract the latest agent response from context
        if message.context:
            # Typically, the agent's response is the last item in the context
            response_content = message.context[-1].content
            await self.websocket.send_text(response_content)
        else:
            # If there's no context, just send a generic message.
            await self.websocket.send_text("No response from the agent.")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtimes = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    runtime = SingleThreadedAgentRuntime()
    runtimes[session_id] = runtime

    # Register agents
    # Register the general agent.
    general_agent_type = await AIAgent.register(
        runtime,
        type=tools.general_agent_topic_type,
        factory=lambda: AIAgent(
            description="A general-purpose agent.",
            system_message=SystemMessage(
                content="You are a versatile agent capable of handling various business workflows. "
                "Assist users by performing tasks, retrieving information, and escalating issues when necessary."
            ),
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

    # Register the support agent.
    support_agent_type = await AIAgent.register(
        runtime,
        type=tools.support_agent_topic_type,
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
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.support_agent_topic_type, agent_type=support_agent_type.type)
    )

    # Register the human agent.
    human_agent_type = await HumanAgent.register(
        runtime,
        type=tools.human_agent_topic_type,
        factory=lambda: HumanAgent(
            description="A human agent.",
            agent_topic_type=tools.human_agent_topic_type,
            user_topic_type=tools.user_topic_type,
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=tools.human_agent_topic_type, agent_type=human_agent_type.type)
    )

    # Register the user agent. The user agent now uses the WebSocketUserAgent
    user_agent_type = await WebSocketUserAgent.register(
        runtime,
        type=tools.user_topic_type,
        factory=lambda: WebSocketUserAgent(
            description="A user agent.",
            user_topic_type=tools.user_topic_type,
            agent_topic_type=tools.general_agent_topic_type,
            websocket=websocket,
        ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=tools.user_topic_type, agent_type=user_agent_type.type))

    # Start the runtime.
    runtime.start()

    # Create a new session for the user by publishing a UserLogin event
    await runtime.publish_message(UserLogin(), topic_id=TopicId(tools.user_topic_type, source=session_id))

    # The server now listens for user messages via the websocket.
    try:
        while True:
            data = await websocket.receive_text()

            # The user's messages are forwarded to the runtime as UserTasks.
            # This simulates the user providing new input.
            # We will publish a UserTask with the user's message context.
            await runtime.publish_message(
                UserTask(context=[UserMessage(content=data, source="User")]),
                topic_id=TopicId(tools.general_agent_topic_type, source=session_id),
            )

    except Exception as e:
        traceback.print_exc()
        print(f"Connection closed: {e}")
    finally:
        await runtime.stop()
        del runtimes[session_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
