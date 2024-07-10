import streamlit as st  # to render the user interface.
from langchain_community.llms import Ollama  # to use Ollama llms in langchain
from langchain_core.prompts import ChatPromptTemplate  # crafts prompts for our llm
from langchain_community.chat_message_histories import\
    StreamlitChatMessageHistory  # stores message history
from langchain_core.tools import tool  # tools for our llm
# to describe tools as a string
from langchain.tools.render import render_text_description
# ensure JSON input for tools
from langchain_core.output_parsers import JsonOutputParser
from operator import itemgetter  # to retrieve specific items in our chain.

import requests
from datetime import datetime, timedelta
import requests
from typing import List
from langchain.chat_models.openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI


load_dotenv()

# model = Ollama(model='mistral:instruct')


model = AzureChatOpenAI(deployment_name="gpt-4o")


class Appointment:
    def __init__(self, **data):
        self.id = data['id']
        self.date_time = data['date_time']
        self.doctor_name = data['doctor_name']


@tool
def get_all_appointments() -> List[Appointment]:
    """Get all appointments, future and past"""
    api = "http://localhost:8000/appointments"
    response = requests.get(api)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to get all appointments.")


@tool
def get_past_appointments():
    """Get past appointments"""
    api = "http://localhost:8000/appointments/past"
    response = requests.get(api)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to get past appointments.")


@tool
def get_future_appointments() -> List[Appointment]:
    """Get future appointments"""
    api = "http://localhost:8000/appointments/future"
    response = requests.get(api)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to get future appointments.")


@tool
def add(first: int, second: int) -> int:
    "Add two integers."
    return first + second


@tool
def multiply(first: int, second: int) -> int:
    """Multiply two integers together."""
    return first * second


@tool
def converse(input: str) -> str:
    "Provide a natural language response using the user input."
    return model.invoke(input)


tools = [add, multiply, converse, get_future_appointments,
         get_past_appointments, get_all_appointments]
rendered_tools = render_text_description(tools)

#####################################################################

system_prompt = f"""You are an assistant that has access to the following set of tools.
Here are the names and descriptions for each tool:

{rendered_tools}
Given the user input, return the name and input of the tool to use.
Return your response as a JSON blob with 'name' and 'arguments' keys.
The value associated with the 'arguments' key should be a dictionary of parameters."""


prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", "{input}")]
)

chain = prompt | model | JsonOutputParser()

# Define a function which returns the chosen tool
# to be run as part of the chain.

###########################################################################


system_prompt_rag = f"""
Assume that today's date is {datetime.today().strftime('%Y-%m-%d')}.
You are an assistant that has access to user's doctor appointments. Answer user's question considering given context."""


prompt_rag = ChatPromptTemplate.from_messages(
    [("system", system_prompt_rag), ("user", "{input}")]
)

chain_rag = prompt_rag | model

#############################################################################


def tool_chain(model_output):
    tool_map = {tool.name: tool for tool in tools}
    chosen_tool = tool_map[model_output["name"]]
    return itemgetter("arguments") | chosen_tool


chain = prompt | model | JsonOutputParser(
) | tool_chain | chain_rag


# Set up message history.
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message(
        "Hello, I can assist your with your doctor appointments, how can I help you today?")

st.title("Chatbot with tools")

# Render the chat history.
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)


# React to user input
if input := st.chat_input("What is up?"):
    # Display user input and save to message history.
    st.chat_message("user").write(input)
    msgs.add_user_message(input)
    # Invoke chain to get reponse.
    response = chain.invoke({'input': input})
    # Display AI assistant response and save to message history.
    st.chat_message("assistant").write(str(response))
    print(response)
    msgs.add_ai_message(response)
