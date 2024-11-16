from fastapi.websockets import WebSocketState
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage  # Removed ToolMessage
import logging
import graypy
import asyncio
from fastapi import WebSocket, WebSocketDisconnect  # Add WebSocketDisconnect import

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add Graypy handler
graylog_handler = graypy.GELFUDPHandler("0.0.0.0", 12202)
logging.getLogger().addHandler(graylog_handler)


# Define the web_search tool
async def web_search(query: str) -> str:
    """Find information on the web"""
    logging.info(f"Web search called with query: {query}")
    # Simulate a web search result
    return "AutoGen is a programming framework for building multi-agent applications."


class ChatSession:
    def __init__(self, websocket, user_proxy_agent):
        self.websocket = websocket
        self.user_proxy_agent = user_proxy_agent
        self.user_id = "user"
        # Remove queues
        # self.input_queue = asyncio.Queue()
        # self.output_queue = asyncio.Queue()

        # Initialize the assistant agent
        self.assistant = AssistantAgent(
            name="assistant",
            model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
            tools=[web_search],  # Added tools
            system_message="""You are a helpful assistant. When you respond with the status, add the word TERMINATE.""",
        )

        # Define termination condition
        self.termination = TextMentionTermination("TERMINATE")

    async def process_message(self, data: str):
        try:
            # Create a RoundRobinGroupChat with the assistant and user proxy agent
            agent_team = RoundRobinGroupChat(
                [self.assistant, self.user_proxy_agent],
                termination_condition=self.termination,
            )

            logging.info(f"Processing task: {data}")

            # Run the team on the task
            result = await agent_team.run(task=data)

            # Handle responses as TextMessage
            if isinstance(result.messages[-1], TextMessage):
                logging.info(f"Response: {result.messages}")
                response = result.messages[-1].content.replace("TERMINATE", "")
                logging.info(f"Response: {response}")
                if self.websocket.client_state != WebSocketState.DISCONNECTED:
                    await self.websocket.send_text(response)
            else:
                logging.warning("Received unknown message type.")
        except WebSocketDisconnect:
            logging.warning("WebSocket disconnected.")
        except Exception as e:
            logging.error(f"Error in process_message: {str(e)}")

    async def run(self):
        try:
            while self.websocket.client_state != WebSocketState.DISCONNECTED:
                # Receive a message from the client
                data = await self.websocket.receive_text()
                await self.process_message(data)
        except WebSocketDisconnect:
            logging.warning("WebSocket disconnected.")
        except Exception as e:
            logging.error(f"Error in run: {str(e)}")
        finally:
            if self.websocket.client_state != WebSocketState.DISCONNECTED:
                await self.websocket.close()
