"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class OrderApproved(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    EVENT_ID_FIELD_NUMBER: builtins.int
    CORRELATION_ID_FIELD_NUMBER: builtins.int
    ORDER_ID_FIELD_NUMBER: builtins.int
    CUSTOMER_ID_FIELD_NUMBER: builtins.int
    CREATED_AT_FIELD_NUMBER: builtins.int
    event_id: builtins.str
    correlation_id: builtins.str
    order_id: builtins.str
    customer_id: builtins.str
    created_at: builtins.str
    def __init__(
        self,
        *,
        event_id: builtins.str = ...,
        correlation_id: builtins.str = ...,
        order_id: builtins.str = ...,
        customer_id: builtins.str = ...,
        created_at: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["correlation_id", b"correlation_id", "created_at", b"created_at", "customer_id", b"customer_id", "event_id", b"event_id", "order_id", b"order_id"]) -> None: ...

global___OrderApproved = OrderApproved