from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class WantedVideoLimitProblemDetails(APIError, AdditionalDataHolder, Parsable):
    """
    Problem response returned when adding wanted videos would exceed the current limit.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Stable machine-readable error code.
    code: Optional[str] = None
    # The detail property
    detail: Optional[str] = None
    # The instance property
    instance: Optional[str] = None
    # Current wanted video limit.
    limit: Optional[int] = None
    # Number of entries that can still be added.
    remaining: Optional[int] = None
    # The status property
    status: Optional[int] = None
    # The title property
    title: Optional[str] = None
    # The type property
    type: Optional[str] = None
    # Current number of non-deleted wanted videos.
    used: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WantedVideoLimitProblemDetails:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WantedVideoLimitProblemDetails
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WantedVideoLimitProblemDetails()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "code": lambda n : setattr(self, 'code', n.get_str_value()),
            "detail": lambda n : setattr(self, 'detail', n.get_str_value()),
            "instance": lambda n : setattr(self, 'instance', n.get_str_value()),
            "limit": lambda n : setattr(self, 'limit', n.get_int_value()),
            "remaining": lambda n : setattr(self, 'remaining', n.get_int_value()),
            "status": lambda n : setattr(self, 'status', n.get_int_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
            "used": lambda n : setattr(self, 'used', n.get_int_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_str_value("code", self.code)
        writer.write_str_value("detail", self.detail)
        writer.write_str_value("instance", self.instance)
        writer.write_int_value("limit", self.limit)
        writer.write_int_value("remaining", self.remaining)
        writer.write_int_value("status", self.status)
        writer.write_str_value("title", self.title)
        writer.write_str_value("type", self.type)
        writer.write_int_value("used", self.used)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def primary_message(self) -> Optional[str]:
        """
        The primary error message.
        """
        return super().message

