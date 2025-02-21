#from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

#Creating Langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"


os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

#--------------Prompt Template--------------------------------------

prompt = ChatPromptTemplate.from_messages([
    ("system","As a helpful assistant, answer the following question"),
    ("user", "Question: {question}")
])

# ----------- Streamlit framework -------------------------------------

st.title("Langchain Demo with LLAMA2")
input_text = st.text_input("Enter your query here...")

llm = Ollama(model = "llama2")
output_parser = StrOutputParser()
chain = prompt|llm|output_parser

if input_text:
    st.write(chain.invoke({'question':input_text}))