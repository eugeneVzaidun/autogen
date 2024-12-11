import uuid
import traceback
import tools
import uvicorn

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocketDisconnect
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import SingleThreadedAgentRuntime, TopicId
from autogen_core.models import UserMessage
from models import UserTask, UserLogin

# Import the initialization function
from workflow import initialize_agents


model_client = OpenAIChatCompletionClient(model="gpt-4o")

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

    # Initialize agents using the workflow module
    await initialize_agents(runtime, session_id, websocket)

    # Start the runtime
    runtime.start()

    # Publish initial UserLogin message
    await runtime.publish_message(UserLogin(), topic_id=TopicId(tools.user_topic_type, source=session_id))

    try:
        while True:
            try:
                data = await websocket.receive_text()
                # The user's messages are published as UserTask events
                await runtime.publish_message(
                    UserTask(context=[UserMessage(content=data, source="User")]),
                    topic_id=TopicId(tools.general_agent_topic_type, source=session_id),
                )
            except WebSocketDisconnect:
                print(f"Client {session_id} disconnected.")
                break
            except Exception as e:
                traceback.print_exc()
                print(f"Connection error for {session_id}: {e}")
                break
    finally:
        await runtime.stop()
        del runtimes[session_id]


if __name__ == "__main__":
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
