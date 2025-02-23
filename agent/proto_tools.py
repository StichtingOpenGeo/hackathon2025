from langchain_core import messages as langgraph_messages

from proto import messages_pb2
from google.protobuf.json_format import ParseDict, MessageToDict


ProtoMessage = messages_pb2.BaseMessage | messages_pb2.HumanMessage | messages_pb2.AIMessage | messages_pb2.SystemMessage | messages_pb2.ToolMessage
LangGraphMessage = langgraph_messages.HumanMessage | langgraph_messages.AIMessage | langgraph_messages.SystemMessage | langgraph_messages.ToolMessage


proto_type_map = {
    "ai": messages_pb2.AIMessage,
    "human": messages_pb2.HumanMessage,
    "system": messages_pb2.SystemMessage,
    "tool": messages_pb2.ToolMessage,
}

langgraph_type_map = {
    "ai": langgraph_messages.AIMessage,
    "human": langgraph_messages.HumanMessage,
    "system": langgraph_messages.SystemMessage,
    "tool": langgraph_messages.ToolMessage,
}


def _langgraph_to_proto(message: LangGraphMessage) -> ProtoMessage:
    proto_cls = proto_type_map[message.type]
    message_data = langgraph_messages.message_to_dict(message)["data"]
    return ParseDict(message_data, proto_cls(), ignore_unknown_fields=True)


def _proto_to_langgraph(message: ProtoMessage) -> LangGraphMessage:
    message_data = MessageToDict(message, preserving_proto_field_name=True)
    langgraph_cls = langgraph_type_map[message.type]
    return langgraph_cls(**message_data)


def serialize(message: LangGraphMessage) -> bytes:
    return _langgraph_to_proto(message).SerializeToString()


def deserialize(data: bytes) -> LangGraphMessage:
    # read first few shared bytes to infer message type
    base_message = messages_pb2.BaseMessage()
    base_message.ParseFromString(data)
    message_cls = proto_type_map[base_message.type]

    message = message_cls()
    message.ParseFromString(data)

    return _proto_to_langgraph(message)
