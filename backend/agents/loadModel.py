from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

import os
from dotenv import load_dotenv
load_dotenv()

llm = None


if os.getenv("USE_LOCAL") == "true":
    print('local model')
    llm = ChatOllama(model="llama3.2:3b", temperature=0)
else:
    print('cloud model')
    llm = ChatGroq(model=os.getenv("GROQ_MODEL"), temperature=0)
