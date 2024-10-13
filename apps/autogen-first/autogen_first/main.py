import os
import autogen
import gradio as gr
import logging

logging.basicConfig(level=logging.DEBUG)


# Function to load configuration from environment variables or a JSON file
def load_config():
    config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")
    if not config_list:
        # Fallback to environment variables if JSON is not provided
        config_list = [
            {
                "api_key": os.environ.get("OPENAI_API_KEY", ""),
                "api_base": os.environ.get("OPENAI_API_BASE", ""),
                "api_type": os.environ.get("OPENAI_API_TYPE", "openai"),
                "api_version": os.environ.get("OPENAI_API_VERSION", "v1"),
                "model": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            }
        ]
    return config_list


# Initialize the Assistant Agent
config_list = load_config()
assistant = autogen.AssistantAgent(name="assistant", llm_config={"config_list": config_list})


def chatbot_reply(message, history):
    """
    Send the user message to the AssistantAgent and get the response.

    Args:
        message (str): The user's input message.
        history (list): The chat history.

    Returns:
        tuple: Updated chat history with the assistant's reply.
    """
    # Append user message to history
    history.append({"role": "user", "content": message})

    try:
        # Get the assistant's response using the correct method
        response = assistant.initiate_chat(message)
    except Exception as e:
        response = f"Error: {str(e)}"

    # Append assistant's response to history
    history.append({"role": "assistant", "content": response})

    return history


def reset_chat():
    """
    Reset the chat history to its initial state.

    Returns:
        list: Initial chat history with a system message.
    """
    return [{"role": "system", "content": "Hello! I am your helpful assistant. How can I help you today?"}]


# Define the Gradio interface
with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# 🧠 Simple AutoGen Q&A Chatbot")
    chatbot = gr.Chatbot(reset_chat, type="messages")
    with gr.Row():
        with gr.Column(scale=4):
            user_input = gr.Textbox(
                show_label=False,
                placeholder="Type your question here...",
            )
        with gr.Column(scale=1):
            send_button = gr.Button("Send")
    clear_button = gr.Button("Clear Chat")

    # Define interactions
    send_button.click(chatbot_reply, inputs=[user_input, chatbot], outputs=[chatbot])
    user_input.submit(chatbot_reply, inputs=[user_input, chatbot], outputs=[chatbot])
    clear_button.click(reset_chat, inputs=None, outputs=[chatbot])

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0")
