import asyncio
import logging
import os
import random
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from aiomqtt import Client
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from websockets import broadcast
from werkzeug.routing import Map, Rule
from websockets.asyncio.router import route

import proto_tools
from agent import session_agent

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

APP_HOST = os.getenv("APP_HOST", "localhost")
APP_PORT = int(os.getenv("APP_PORT", "8765"))


connections = {}


logger = logging.getLogger("agent.ws_server")


async def publish_messages(client, websocket, session_id):
    """Receives websocket messages and publishes them on the session specific topic."""
    async for ws_message in websocket:
        message = HumanMessage(
            id=str(uuid.uuid4()),
            content=ws_message,
            name="user",
        )
        await client.publish(
            f"sessions/{session_id}",
            proto_tools.serialize(message),
            qos=2,
        )
        logger.info(f"message published {message=} {session_id=}")
        async for message, metadata in agent_response(message, session_id):
            await client.publish(
                f"sessions/{session_id}",
                proto_tools.serialize(message),
                qos=2,
            )
            logger.info(f"message published {message=} {session_id=}")


async def subscribe_messages(client, _, session_id):
    """Subscribes to mqtt session topic and broadcasts to all websockets connected to the session."""
    await client.subscribe(f"sessions/{session_id}", qos=2)
    async for mqtt_message in client.messages:
        message = proto_tools.deserialize(mqtt_message.payload)
        # skip messages that were sent by the user itself
        if message.name == "user":
            continue
        session_connections = [
            connection
            for connection, meta in connections.items()
            if meta['session_id'] == session_id
        ]
        broadcast(session_connections, mqtt_message.payload)


async def agent_response(user_message, session_id) -> AsyncGenerator[Any]:
    async with session_agent(session_id) as (graph, config):
        stream = graph.astream(
            {"messages": [user_message]},
            stream_mode="messages",
            config=config,
        )
        async for item in stream:
            yield item


async def mock_message_producer():
    """On random interval, send an announcement to a random session (if any active)"""
    while True:
        await asyncio.sleep(random.randint(10, 60))
        _, metadata = next(iter(connections.items()), (None, None))
        if metadata is None: # no active sessions
            continue

        async with Client(MQTT_BROKER, MQTT_PORT) as client:
            message = AIMessage(content="There is a delay on your route!")
            session_id = metadata['session_id']

            async with session_agent(session_id) as (graph, config):
                await graph.aupdate_state(config, {"messages": [message]}, as_node="agent")

            await client.publish(
                f"sessions/{session_id}",
                proto_tools.serialize(message),
                qos=2,
            )
            logger.info(f"message published {message=} {session_id=}")


async def channel_handler(websocket, session_id):
    try:
        connections[websocket] = {"session_id": session_id}
        async with Client(MQTT_BROKER, MQTT_PORT) as client:
            logger.info(f"client connected {session_id=}")
            tasks = [
                asyncio.create_task(publish_messages(client, websocket, session_id)),
                asyncio.create_task(subscribe_messages(client, websocket, session_id)),
            ]
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
    finally:
        logger.info(f"client disconnected {session_id=}")
        del connections[websocket]


url_map = Map([Rule("/sessions/<session_id>", endpoint=channel_handler)])


async def main():
    async with route(url_map, APP_HOST, APP_PORT) as server:
        await asyncio.gather(
            server.serve_forever(),
            mock_message_producer(),
        )

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

