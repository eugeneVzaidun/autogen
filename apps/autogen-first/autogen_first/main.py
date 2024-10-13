# import autogen
# import random
# import string


# def generate_random_string(length=10):
#     letters = string.ascii_letters + string.digits
#     return "".join(random.choice(letters) for i in range(length))


# # import OpenAI API key
# config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")

# # create the assistant agent
# assistant = autogen.AssistantAgent(name="assistant", llm_config={"config_list": config_list})


# assistant.register_for_llm(
#     name="generate_random_string",
#     description="A tool to generate a random string.",
# )(generate_random_string)

# # Create the user proxy agent
# user_proxy = autogen.UserProxyAgent(name="UserProxy", code_execution_config={"work_dir": "results"})

# user_proxy.register_for_execution(
#     name="generate_random_string",
# )(generate_random_string)

# # Start the conversation
# user_proxy.initiate_chat(assistant, message="Tell me a name of first US president. And after generata a random string.")


import gradio as gr


def echo(message, history, system_prompt, tokens):
    return message


with gr.Blocks() as demo:

    gr.ChatInterface(echo, type="messages", fill_height=True, fill_width=True)

demo.launch()
