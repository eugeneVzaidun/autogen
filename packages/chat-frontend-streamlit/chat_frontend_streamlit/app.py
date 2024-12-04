import streamlit as st
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosed
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
# Set the page configuration
st.set_page_config(page_title="Kruso Agentic Experience", page_icon="💬", layout="centered")

st.title("💬 Kruso Agentic Experience")
# Initialize chat sessions in session state
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Initialize current session ID
if "current_session" not in st.session_state:
    st.session_state.current_session = None


# Function to create a new chat session
def create_new_session():
    session_id = str(uuid.uuid4())[:8]  # Shorten UUID for readability
    st.session_state.chat_sessions[session_id] = {"messages": [], "websocket": None, "ws_connected": False}
    st.session_state.current_session = session_id
    connect_websocket(session_id)


# Function to connect WebSocket for a session
def connect_websocket(session_id):
    if st.session_state.chat_sessions[session_id]["ws_connected"]:
        return
    base_url = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")
    url = f"{base_url}/{session_id}"
    try:
        st.session_state.chat_sessions[session_id]["websocket"] = connect(url)
        st.session_state.chat_sessions[session_id]["ws_connected"] = True
    except Exception as e:
        st.sidebar.error(f"❌ Error connecting to WebSocket for session {session_id}: {e}")
        st.session_state.chat_sessions[session_id]["ws_connected"] = False


# Sidebar for session management
with st.sidebar:
    st.header("🗂️ Chat Sessions")

    # List existing sessions
    session_ids = list(st.session_state.chat_sessions.keys())
    if session_ids:
        selected_session = st.radio("Select a session:", ["Create New Session"] + session_ids)
        if selected_session == "Create New Session":
            if st.button("🆕 Create New Session"):
                create_new_session()
        else:
            st.session_state.current_session = selected_session
    else:
        st.info("No chat sessions found. Click below to create one.")
        if st.button("🆕 Create New Session"):
            create_new_session()

    st.markdown("---")

    # Optional: Display session details or allow deletion
    if st.session_state.current_session:
        st.write(f"**Current Session:** {st.session_state.current_session}")
        if st.button("🗑️ Delete Current Session"):
            del st.session_state.chat_sessions[st.session_state.current_session]
            st.session_state.current_session = None

# Check if a session is selected
if not st.session_state.current_session:
    st.warning("Please create or select a chat session from the sidebar.")
    st.stop()

current_session = st.session_state.current_session
current_chat = st.session_state.chat_sessions[current_session]

# Display chat messages from the current session
for msg in current_chat["messages"]:
    with st.chat_message(msg["type"]):
        st.markdown(msg["content"])


# Function to send messages via WebSocket
def send_via_websocket(message, session_id):
    session = st.session_state.chat_sessions[session_id]
    if not session.get("ws_connected", False):
        return "❌ WebSocket is not connected."

    try:
        websocket = session["websocket"]
        websocket.send(message)
        response = websocket.recv()
        return response
    except ConnectionClosed:
        session["ws_connected"] = False
        return "❌ Connection closed unexpectedly."
    except Exception as e:
        return f"❌ Error: {e}"


# Capture user input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    current_chat["messages"].append({"type": "user", "content": user_input})

    # Send the message to the WebSocket backend and get the response
    with st.spinner("🤖 Thinking..."):
        assistant_response = send_via_websocket(user_input, current_session)

    # Display assistant response
    st.chat_message("assistant").markdown(assistant_response)
    current_chat["messages"].append({"type": "assistant", "content": assistant_response})
