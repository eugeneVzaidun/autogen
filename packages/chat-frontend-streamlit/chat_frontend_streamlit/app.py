import streamlit as st
from websockets.sync.client import connect
import uuid

# Set the page configuration
st.set_page_config(page_title="Kruso Agentic Expirience", page_icon="💬", layout="centered")

st.title("💬 Kruso Agentic Expirience")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []


def send_via_websocket(message):
    unique_id = uuid.uuid4()
    url = f"ws://localhost:8000/ws/{unique_id}"
    try:
        with connect(url) as websocket:
            websocket.send(message)
            response = websocket.recv()
            return response
    except Exception as e:
        return f"❌ Error: {e}"


# Display chat messages from history
for msg in st.session_state.messages:
    with st.chat_message(msg["type"]):
        st.markdown(msg["content"])

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
