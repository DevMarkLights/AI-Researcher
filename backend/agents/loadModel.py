from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

import os
from dotenv import load_dotenv
load_dotenv()

llm_small = None
llm_large = None

if os.getenv("USE_LOCAL") == 'true':
    print('local model')
    llm_small = ChatOllama(model="llama3.2:3b", temperature=0, num_predict=4096, num_ctx=4096)
    llm_large = ChatOllama(model="llama3.1:8b", temperature=0, num_predict=4096, num_ctx=4096)
else:
    print('cloud model')
    llm_small = ChatGroq(model=os.getenv("GROQ_MODEL_SMALL"), temperature=0, max_tokens=4096)
    llm_large = ChatGroq(model=os.getenv("GROQ_MODEL_LARGE"), temperature=0, max_tokens=4096)
