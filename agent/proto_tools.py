
from langchain_core import messages as langgraph_messages

from proto import messages_pb2
from google.protobuf.json_format import ParseDict, MessageToDict


ProtoMessage = messages_pb2.BaseMessage | messages_pb2.HumanMessage | messages_pb2.AIMessage | messages_pb2.SystemMessage | messages_pb2.ToolMessage
LangGraphMessage = langgraph_messages.HumanMessage | langgraph_messages.AIMessage | langgraph_messages.SystemMessage | langgraph_messages.ToolMessage

PB_TYPE_MAP = {
    messages_pb2.human: messages_pb2.HumanMessage,
    messages_pb2.human_chunk: messages_pb2.HumanMessage,
    messages_pb2.ai: messages_pb2.AIMessage,
    messages_pb2.ai_chunk: messages_pb2.AIMessage,
    messages_pb2.system: messages_pb2.SystemMessage,
    messages_pb2.system_chunk: messages_pb2.SystemMessage,
    messages_pb2.tool: messages_pb2.ToolMessage,
    messages_pb2.tool_chunk: messages_pb2.ToolMessage,
}

LG_TYPE_MAP = {
    messages_pb2.human: langgraph_messages.HumanMessage,
    messages_pb2.human_chunk: langgraph_messages.HumanMessageChunk,
    messages_pb2.ai: langgraph_messages.AIMessage,
    messages_pb2.ai_chunk: langgraph_messages.AIMessageChunk,
    messages_pb2.system: langgraph_messages.SystemMessage,
    messages_pb2.system_chunk: langgraph_messages.SystemMessageChunk,
    messages_pb2.tool: langgraph_messages.ToolMessage,
    messages_pb2.tool_chunk: langgraph_messages.ToolMessageChunk,
}

def _message_type_value(message: LangGraphMessage) -> messages_pb2.MessageType:
    type_name = message.type.removesuffix("MessageChunk").lower()
    type_name += "_chunk" if message.type.endswith("MessageChunk") else ""
    return messages_pb2.MessageType.Value(type_name)


def serialize(message: LangGraphMessage) -> bytes:
    message_type = _message_type_value(message)
    pb_type = PB_TYPE_MAP[message_type]
    message_data = message.model_dump(exclude={"type"})
    message_proto = ParseDict(
        {"type": message_type, **message_data},
        pb_type(),
        ignore_unknown_fields=True
    )
    return message_proto.SerializeToString()


def deserialize(data: bytes) -> LangGraphMessage:
    # read first few shared bytes to infer message type
    base_message = messages_pb2.BaseMessage()
    base_message.ParseFromString(data)
    pb_type = PB_TYPE_MAP[base_message.type]

    message = pb_type()
    message.ParseFromString(data)
    message_data = MessageToDict(message, preserving_proto_field_name=True)
    message_data.pop("type")

    lg_type = LG_TYPE_MAP[base_message.type]
    return lg_type(**message_data)
