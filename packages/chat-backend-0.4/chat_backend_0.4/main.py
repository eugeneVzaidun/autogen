from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from autogen_chat import ChatSession
import uvicorn

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[ChatSession] = []

    async def connect(self, chat_session: ChatSession):
        await chat_session.websocket.accept()
        self.active_connections.append(chat_session)

    async def disconnect(self, chat_session: ChatSession):
        chat_session.input_queue.put_nowait("TERMINATE")
        print(f"autogen_chat {chat_session.user_id} disconnected")
        self.active_connections.remove(chat_session)


manager = ConnectionManager()


@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    chat_session = ChatSession(websocket)
    await manager.connect(chat_session)
    try:
        await chat_session.run()
    except WebSocketDisconnect:
        print(f"Client {chat_id} disconnected")
    except Exception as e:
        print(f"Error in websocket_endpoint: {str(e)}")
    finally:
        await manager.disconnect(chat_session)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
