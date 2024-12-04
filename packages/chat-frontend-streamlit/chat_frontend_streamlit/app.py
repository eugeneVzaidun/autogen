import streamlit as st
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosed
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
# Set the page configuration
st.set_page_config(page_title="Kruso Agentic Experience", page_icon="💬", layout="centered")

st.title("💬 Kruso Agentic Experience")

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize WebSocket connection state
if "ws_connected" not in st.session_state:
    st.session_state.ws_connected = False


# Function to connect WebSocket
def connect_websocket():
    if st.session_state.ws_connected:
        return
    base_url = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")
    try:
        st.session_state.websocket = connect(base_url)
        st.session_state.ws_connected = True
    except Exception as e:
        st.sidebar.error(f"❌ Error connecting to WebSocket: {e}")
        st.session_state.ws_connected = False


# Connect WebSocket on app start
connect_websocket()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["type"]):
        st.markdown(msg["content"])


# Function to send messages via WebSocket
def send_via_websocket(message):
    if not st.session_state.ws_connected:
        return "❌ WebSocket is not connected."

    try:
        websocket = st.session_state.websocket
        websocket.send(message)
        response = websocket.recv()
        return response
    except ConnectionClosed:
        st.session_state.ws_connected = False
        return "❌ Connection closed unexpectedly."
    except Exception as e:
        return f"❌ Error: {e}"


# Capture user input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"type": "user", "content": user_input})

    # Send the message to the WebSocket backend and get the response
    with st.spinner("🤖 Thinking..."):
        assistant_response = send_via_websocket(user_input)

    # Display assistant response
    st.chat_message("assistant").markdown(assistant_response)
    st.session_state.messages.append({"type": "assistant", "content": assistant_response})
