import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional, List, Any, AsyncGenerator

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.runnables.schema import StreamEvent
from langchain_core.tools import tool, BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent, ToolNode
import requests

import api

# System message defining the chatbot's role and behavior
SYSTEM_PROMPT = SystemMessage(
    """
    Je bent een behulpzame assistent die helpt navigeren in het openbaar vervoer. 
    Je geeft beknopt maar vriendelijk antwoord.
    Beëindig het gesprek niet vroegtijdig.
    """
)


@tool
def get_bike_count():
    """Retrieve the number of available rental bikes (OV-fiets) at all stations."""

    return api.get_bike_availability()

@tool
def get_transit_lines(linenumber: str):
    """Retrieve the next departure time for a specified transit line number."""

    try:
        lines_requests = requests.get("http://v0.ovapi.nl/line/")
        all_lines = lines_requests.json()
        candidates = [i for i in all_lines.items() if i[1]['LinePublicNumber'] == linenumber]
        lines = list(set(map(lambda x: f"Lijn {x[1]['LinePublicNumber']} naar {x[1]['DestinationName50']} (line id {x[0]})", candidates)))
        return f"Ik heb meerdere opties voor lijn {linenumber}, bedoelde je {", ".join(lines)}"
    except Exception as e:
        print(e)
        raise e

@tool
def get_departure_times(line_id: str):
    """Retrieve the next departure time for a specified transit line"""
    try:
        line_request = requests.get("http://v0.ovapi.nl/line/"+line_id)
        line = line_request.json()[line_id]
        rit = list(line['Actuals'].items())[0][1]
        return f"De bus vertrekt om {rit['TargetDepartureTime']} naar {line['Line']['DestinationName50']}"
    except Exception as e:
        print(e)
        raise e


class Executor:
    def __init__(
        self,
        *,
        model: Optional[BaseChatModel] = None,
        tools: List[BaseTool] = None,
        config: Optional[dict] = None,
        checkpointer: Optional[BaseCheckpointSaver | Any] = None,
    ):
        """Initialize the executor with a language model-powered agent."""
        # To use groq ChatGroq(temperature=0.2, model_name="llama3-8b-8192") #
        self.model = model or ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.tools = tools or [get_departure_times, get_bike_count, get_transit_lines]
        self.config = config or {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            }
        }
        self.checkpointer = checkpointer or AsyncSqliteSaver.from_conn_string("checkpoints.db")

    @asynccontextmanager
    async def agent_context(self):
        async with self.checkpointer as saver:
            yield create_react_agent(
                model=self.model,
                tools=ToolNode(self.tools),
                prompt=SYSTEM_PROMPT,
                checkpointer=saver,
            )

    async def handle_event(self, event: StreamEvent):
        """Handles incoming events dynamically by invoking the appropriate method."""
        event_name = event.get("event")
        handler = getattr(self, event_name, None)
        logging.debug("Handling event: %s", event)
        if handler:
            await handler(event)

    async def on_chat_model_stream(self, event):
        """Handles streaming responses from the chatbot."""
        chunk = event["data"].get("chunk")
        if chunk:
            print(chunk.content, end="")
            if chunk.response_metadata.get("finish_reason") == "stop":
                print()

    async def run(self):
        """Runs the chatbot in an interactive loop."""
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting...")
                break
            await self.query_agent(user_input)

    async def query_agent(self, message: str):
        """Sends user input to the chatbot and processes its responses."""
        async with self.agent_context() as agent:
            async for event in agent.astream_events(
                {"messages": [message]},
                config=self.config,
                version="v2",
            ):
                await self.handle_event(event)

            return await agent.aget_state(self.config)


if __name__ == "__main__":
    load_dotenv()
    executor = Executor()
    asyncio.run(executor.run())


@asynccontextmanager
async def session_agent(session_id):
    config = {"configurable": {"thread_id": session_id}}
    async with Executor(config=config).agent_context() as graph:
        yield graph, config


async def agent_response(message, session_id) -> AsyncGenerator[BaseMessage, None]:
    async with session_agent(session_id) as (graph, config):
        stream = graph.astream(
            {"messages": [message]},
            stream_mode="messages",
            config=config,
        )
        async for item in stream:
            yield item


async def update_session_state(session_id, state, **kwargs):
    async with session_agent(session_id) as (graph, config):
        await graph.aupdate_state(config, state, **kwargs)
