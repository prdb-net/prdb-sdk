from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class RateLimitWindowStatus(AdditionalDataHolder, Parsable):
    """
    Rate limit status for a single time window.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Maximum number of requests allowed within this window.
    limit: Optional[int] = None
    # Number of requests remaining before the limit is reached.
    remaining: Optional[int] = None
    # Seconds until the oldest request in the window expires, reducing the used count by one.
    resets_in_seconds: Optional[int] = None
    # Number of requests made within the current window.
    used: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RateLimitWindowStatus:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RateLimitWindowStatus
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RateLimitWindowStatus()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "limit": lambda n : setattr(self, 'limit', n.get_int_value()),
            "remaining": lambda n : setattr(self, 'remaining', n.get_int_value()),
            "resetsInSeconds": lambda n : setattr(self, 'resets_in_seconds', n.get_int_value()),
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
        writer.write_int_value("limit", self.limit)
        writer.write_int_value("remaining", self.remaining)
        writer.write_int_value("resetsInSeconds", self.resets_in_seconds)
        writer.write_int_value("used", self.used)
        writer.write_additional_data_value(self.additional_data)
    

