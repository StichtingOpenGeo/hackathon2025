import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from agent import Executor


@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    
    answer1 = cl.Message(content="")
    executor = Executor(config=config)
    async with executor.agent_context() as graph:
        message_stream = graph.astream(
            {"messages": [HumanMessage(content=msg.content)]},
            stream_mode="messages",
            config=RunnableConfig(callbacks=[cb], **config)
        )
        async for msg, metadata in message_stream:
            if msg.content and isinstance(msg, AIMessage):
                await answer1.stream_token(msg.content)

    answer2 = cl.Message(content="")
    executor = Executor(config=config)
    async with executor.agent_context() as graph:
        message_stream = graph.astream(
            {"messages": [HumanMessage(content=msg.content)]},
            stream_mode="messages",
            config=RunnableConfig(callbacks=[cb], **config)
        )
        async for msg, metadata in message_stream:
            if msg.content and isinstance(msg, AIMessage):
                await answer2.stream_token(msg.content)

    await answer1.send()
    await answer2.send()
