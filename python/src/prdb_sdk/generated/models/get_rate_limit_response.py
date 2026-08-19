from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .rate_limit_window_status import RateLimitWindowStatus

@dataclass
class GetRateLimitResponse(AdditionalDataHolder, Parsable):
    """
    Current rate limit status for the authenticated user.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Rate limit status for a single time window.
    hourly: Optional[RateLimitWindowStatus] = None
    # Always true. Rate limiting is enforced unconditionally; when it cannot be enforced the APIanswers 503 instead of returning this document. Kept for compatibility with clients thatread the field.
    is_enforced: Optional[bool] = None
    # Rate limit status for a single time window.
    monthly: Optional[RateLimitWindowStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetRateLimitResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetRateLimitResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetRateLimitResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .rate_limit_window_status import RateLimitWindowStatus

        from .rate_limit_window_status import RateLimitWindowStatus

        fields: dict[str, Callable[[Any], None]] = {
            "hourly": lambda n : setattr(self, 'hourly', n.get_object_value(RateLimitWindowStatus)),
            "isEnforced": lambda n : setattr(self, 'is_enforced', n.get_bool_value()),
            "monthly": lambda n : setattr(self, 'monthly', n.get_object_value(RateLimitWindowStatus)),
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
        writer.write_object_value("hourly", self.hourly)
        writer.write_bool_value("isEnforced", self.is_enforced)
        writer.write_object_value("monthly", self.monthly)
        writer.write_additional_data_value(self.additional_data)
    

