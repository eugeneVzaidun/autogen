from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.task import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models import OpenAIChatCompletionClient
import asyncio


class ChatSession:
    def __init__(self, websocket):
        self.websocket = websocket
        self.user_id = "user"
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

        # Initialize the assistant agent
        self.assistant = AssistantAgent(
            name="assistant",
            model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"),
            system_message="""You are a helpful assistant. When you respond with the status, add the word TERMINATE.""",
        )

        # Define termination condition
        self.termination = TextMentionTermination("TERMINATE")

    async def send_messages(self):
        try:
            while True:
                # Wait for a message to send
                message = await self.output_queue.get()
                if message == "DO_FINISH":
                    break
                if not isinstance(message, str):
                    message = str(message)
                await self.websocket.send_text(message)
        except Exception as e:
            print(f"Error in send_messages: {str(e)}")
        finally:
            if not self.websocket.client_state.closed:
                await self.websocket.close()

    async def receive_messages(self):
        try:
            while True:
                # Receive a message from the client
                data = await self.websocket.receive_text()
                if data == "DO_FINISH":
                    await self.input_queue.put("DO_FINISH")
                    await self.output_queue.put("DO_FINISH")
                    break
                await self.input_queue.put(data)
        except Exception as e:
            print(f"Error in receive_messages: {str(e)}")
        finally:
            if not self.websocket.client_state.closed:
                await self.websocket.close()

    async def process_messages(self):
        try:
            # Create a RoundRobinGroupChat with the assistant
            agent_team = RoundRobinGroupChat(
                [self.assistant],
                termination_condition=self.termination,
            )

            while True:
                # Get the user's message from the input queue
                task = await self.input_queue.get()
                if task == "DO_FINISH":
                    break

                # Run the team on the task
                result = await agent_team.run(task=task)

                # Put the assistant's reply into the output queue
                print(result.messages)
                await self.output_queue.put(result.messages[-2].content)
        except Exception as e:
            print(f"Error in process_messages: {str(e)}")
        finally:
            await self.output_queue.put("DO_FINISH")

    async def run(self):
        # Create tasks for sending, receiving, and processing messages
        send_task = asyncio.create_task(self.send_messages())
        receive_task = asyncio.create_task(self.receive_messages())
        process_task = asyncio.create_task(self.process_messages())

        # Wait for the receive task to finish (e.g., client disconnects)
        await receive_task

        # Cancel other tasks if they are still running
        if not send_task.done():
            send_task.cancel()
        if not process_task.done():
            process_task.cancel()

        # Ensure tasks are completed
        await asyncio.gather(send_task, process_task, return_exceptions=True)
