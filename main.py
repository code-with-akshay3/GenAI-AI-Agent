# this code support for the frontend and backend both

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key= GROQ_API_KEY
)

search_tool = TavilySearchResults(
    max_results=5,
    tavily_api_key=TAVILY_API_KEY
)

tools = [search_tool]

user_memories = {}

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful AI Assistant.Use Tavily Search whenever web information is needed.
            Remember previous messages and behave like ChatGPT."""
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

class ChatRequest(BaseModel):
    user_id: str
    question: str

@app.post("/chat")
async def chat(req: ChatRequest):

    if req.user_id not in user_memories:

        user_memories[req.user_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    memory = user_memories[req.user_id]

    chat_history = memory.load_memory_variables({})["chat_history"]

    result = agent_executor.invoke(
        {
            "input": req.question,
            "chat_history": chat_history
        }
    )

    answer = result["output"]

    memory.save_context(
        {"input": req.question},
        {"output": answer}
    )
    return {
        "answer": answer
    }

@app.get("/")
def home():
    return {
        "message": "AI Agent Running"
    }





# this code only for the backend purpose

# from fastapi import FastAPI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import os

# from langchain_groq import ChatGroq
# from langchain.memory import ConversationBufferMemory
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain_community.tools.tavily_search import TavilySearchResults

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# app = FastAPI(title="AI Agent Backend")

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     api_key=GROQ_API_KEY
# )

# search_tool = TavilySearchResults(
#     max_results=5,
#     tavily_api_key=TAVILY_API_KEY
# )

# tools = [search_tool]

# user_memories = {}

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             """
#             You are a helpful AI Assistant.

#             Use Tavily Search whenever web information is required.

#             Remember previous conversations and answer accordingly.
#             """
#         ),
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("human", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ]
# )

# agent = create_tool_calling_agent(
#     llm=llm,
#     tools=tools,
#     prompt=prompt
# )

# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True
# )

# class ChatRequest(BaseModel):
#     user_id: str
#     question: str

# @app.post("/chat")
# async def chat(req: ChatRequest):

#     if req.user_id not in user_memories:

#         user_memories[req.user_id] = ConversationBufferMemory(
#             memory_key="chat_history",
#             return_messages=True
#         )

#     memory = user_memories[req.user_id]

#     chat_history = memory.load_memory_variables({})["chat_history"]

#     result = agent_executor.invoke(
#         {
#             "input": req.question,
#             "chat_history": chat_history
#         }
#     )

#     answer = result["output"]

#     memory.save_context(
#         {"input": req.question},
#         {"output": answer}
#     )

#     return {
#         "answer": answer
#     }

# @app.get("/")
# def home():
#     return {
#         "status": "running",
#         "message": "AI Agent Backend Running Successfully"
#     }
