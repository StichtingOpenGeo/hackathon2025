# OpenOV Agent

## Prerequisites

- Python 3.12
- UV (https://docs.astral.sh/uv/#getting-started)

## Quickstart

- Clone this repository (`e.g. git clone git@github.com:StichtingOpenGeo/hackathon2025.git`) and `cd` into the "agent" folder.
- Install the dependencies with uv: `uv sync`
- Copy the `.env.example` file to `.env` and fill in the required values, remove LANGSMITH variables completely if you are not going to use it.
- Run the app: `uv run chainlit run app.py -w`
- Visit the app in your browser: `http://localhost:8000`


## Protobuf

Serializing and deserializing data is done using Protobuf. Generating the python files can be done with the following command:

```bash
make protoc
```

After running this command, the Python files will be generated in the `proto` folder and are ready to be imported.

In the `proto_tools.py` module, you can find functions to convert langgraph messages to protobuf and vice versa.

A pseudo example of how to use the protobuf files:

```python
import paho.mqtt.client as mqtt
import proto_tools
import agent

client = mqtt.Client()
executor = agent.Executor()

async with executor.agent_context() as graph:
    async for msg, metadata in graph.astream(...):
        # serialize langgraph message to protobuf
        message_bytes = proto_tools.serialize(msg.content)
        
        # publish serialized message to mqtt topic
        client.publish("thread", message_bytes, ...)
```
