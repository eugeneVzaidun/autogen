from dataclasses import dataclass
from autogen_core import (
    SingleThreadedAgentRuntime,
    AgentId,
    MessageContext,
    message_handler,
    RoutedAgent,
)
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from autogen_ext.models import OpenAIChatCompletionClient
import traceback
import uvicorn
import uuid
from autogen_core.components.models import SystemMessage, UserMessage


@dataclass
class TextMessage:
    content: str
    source: str


model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
)


class MyAgent(RoutedAgent):
    def __init__(self, websocket: WebSocket):
        super().__init__("MyAgent")
        self.websocket = websocket
        self._model_client = model_client
        self._system_message = SystemMessage(content="You are personal assistant, good in answering generic questions.")

    @message_handler
    async def on_text_message(self, message: UserMessage, ctx: MessageContext) -> None:
        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=message.content, source=self.id.key)],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        assert isinstance(response, str)
        await self.websocket.send_text(response)


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

    await MyAgent.register(runtime, "my_agent", lambda: MyAgent(websocket=websocket))
    agent_id = AgentId("my_agent", "default")
    runtime.start()

    try:
        while True:
            data = await websocket.receive_text()
            await runtime.send_message(UserMessage(content=data, source=session_id), agent_id)
    except Exception as e:
        # print full traceback

        traceback.print_exc()
        print(f"Connection closed: {e}")
    finally:
        await runtime.stop()
        del runtimes[session_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
