from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage  # Removed ToolMessage
import logging
import graypy
import asyncio

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
    def __init__(self, websocket):
        self.websocket = websocket
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
        self.termination = (
            TextMentionTermination("TERMINATE") | TextMentionTermination("DO_FINISH") | TextMentionTermination("STOP")
        )

    async def process_messages(self):
        try:
            # Create a RoundRobinGroupChat with the assistant
            agent_team = RoundRobinGroupChat(
                [self.assistant],
                termination_condition=self.termination,
            )

            while True:
                # Receive a message from the client
                data = await self.websocket.receive_text()
                if data == "DO_FINISH":
                    break

                logging.info(f"Processing task: {data}")

                # Run the team on the task
                result = await agent_team.run(task=data)

                # Handle responses as TextMessage
                if isinstance(result.messages[-1], TextMessage):
                    logging.info(f"Response: {result.messages}")
                    response = result.messages[-1].content.replace("TERMINATE", "")
                    logging.info(f"Response: {response}")
                    await self.websocket.send_text(response)
                else:
                    logging.warning("Received unknown message type.")
        except Exception as e:
            logging.error(f"Error in process_messages: {str(e)}")
        finally:
            await self.websocket.close()

    async def run(self):
        # Run message processing directly
        await self.process_messages()
