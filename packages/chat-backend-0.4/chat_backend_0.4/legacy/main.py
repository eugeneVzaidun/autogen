from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from autogen_chat import ChatSession
import uvicorn
import logging

# import graypy

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add Graypy handler
# graylog_handler = graypy.GELFUDPHandler("0.0.0.0", 12202)
# logging.getLogger().addHandler(graylog_handler)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[ChatSession] = []

    async def connect(self, chat_session: ChatSession):
        await chat_session.websocket.accept()
        self.active_connections.append(chat_session)
        logging.info(f"New connection added. Total connections: {len(self.active_connections)}")

    async def disconnect(self, chat_session: ChatSession):
        logging.info(f"autogen_chat {chat_session.user_id} disconnected")
        self.active_connections.remove(chat_session)
        logging.info(f"Connection removed. Total connections: {len(self.active_connections)}")


manager = ConnectionManager()


@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    chat_session = ChatSession(websocket)
    await manager.connect(chat_session)
    try:
        await chat_session.run()
    except WebSocketDisconnect:
        logging.warning(f"Client {chat_id} disconnected")
    except Exception as e:
        logging.error(f"Error in websocket_endpoint: {str(e)}")
    finally:
        await manager.disconnect(chat_session)
        # Removed queue-related code


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
