import json
import sqlite3
import uuid
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel

import agent

load_dotenv()

app = FastAPI()

CHAT_FILE = 'chat.db'
CHECKPOINTER_FILE = 'checkpoints.db'


class ChatState(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]

def init_db():
    """Create the database and sessions table if not exists."""
    conn = sqlite3.connect(CHAT_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            messages TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# Database helper functions
def get_session_messages(session_id: str):
    """Retrieve messages for a session from SQLite."""
    conn = sqlite3.connect(CHAT_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT messages FROM sessions WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else []

def save_session_messages(session_id: str, messages: List[Dict[str, Any]]):
    """Save or update session messages in SQLite."""
    conn = sqlite3.connect(CHAT_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (session_id, messages) VALUES (?, ?) ON CONFLICT(session_id) DO UPDATE SET messages = ?",
                   (session_id, json.dumps(messages), json.dumps(messages)))
    conn.commit()
    conn.close()

def convert_to_openai_format(messages):
    """Converts LangChain messages to OpenAI-compatible format."""
    openai_messages = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            role = f"type::{msg.type}"

        if role == "user" or role == "assistant":
            openai_messages.append({"role": role, "content": msg.content})

    return openai_messages

@app.post("/start_session")
async def start_session():
    session_id = str(uuid.uuid4())
    save_session_messages(session_id, [])  # Initialize with empty chat history
    return {"session_id": session_id}


@app.post("/chat")
async def chat(chat_state: ChatState):
    session_id = chat_state.session_id

    messages = get_session_messages(session_id)

    if messages is None:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Append new user message
    messages.append({"role": "user", "content": chat_state.messages[-1]['content']})

    # Run through LangGraph
    executor = agent.Executor(
        config={"configurable": {"thread_id": session_id}},
        checkpointer=AsyncSqliteSaver.from_conn_string(CHECKPOINTER_FILE),
    )

    graph_state = await executor.query_agent(chat_state.messages[-1]['content'])

    # Save updated session messages
    save_session_messages(session_id, messages := convert_to_openai_format(graph_state.values["messages"]))

    return {"session_id": session_id, "messages": messages}
