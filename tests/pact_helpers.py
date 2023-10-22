from typing import TypeVar, cast

from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message as ProtoMessage
from pact.matchers import Matcher, get_generated_values

ProtoType = TypeVar("ProtoType", bound=ProtoMessage)


def create_proto_from_pact(proto_class: type[ProtoType], expected_message: dict | Matcher) -> ProtoType:
    generated_values = cast(dict, get_generated_values(expected_message))
    return ParseDict(generated_values, proto_class())


def proto_to_dict(data: ProtoMessage) -> dict:
    return MessageToDict(data, preserving_proto_field_name=True)
