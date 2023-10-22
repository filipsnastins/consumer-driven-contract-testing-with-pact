from typing import TypeVar, cast

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message as ProtoMessage
from pact.matchers import get_generated_values

ProtoType = TypeVar("ProtoType", bound=ProtoMessage)


def create_proto_from_pact(proto_class: type[ProtoType], expected_event: dict) -> ProtoType:
    generated_values = cast(dict, get_generated_values(expected_event))
    return proto_class(**generated_values)


def proto_to_dict(data: ProtoMessage) -> dict:
    return MessageToDict(data, preserving_proto_field_name=True)
