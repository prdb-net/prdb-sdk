from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .report_video_user_image_request_reason import ReportVideoUserImageRequest_reason

@dataclass
class ReportVideoUserImageRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The details property
    details: Optional[str] = None
    # Allowed values: NotRelatedToVideo, SpamOrPromotional, OffensiveOrProhibited, DuplicateOrLowQuality, MisleadingOrWrongPreview, CopyrightConcern, Other.
    reason: Optional[ReportVideoUserImageRequest_reason] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ReportVideoUserImageRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ReportVideoUserImageRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ReportVideoUserImageRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .report_video_user_image_request_reason import ReportVideoUserImageRequest_reason

        from .report_video_user_image_request_reason import ReportVideoUserImageRequest_reason

        fields: dict[str, Callable[[Any], None]] = {
            "details": lambda n : setattr(self, 'details', n.get_str_value()),
            "reason": lambda n : setattr(self, 'reason', n.get_enum_value(ReportVideoUserImageRequest_reason)),
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
        writer.write_str_value("details", self.details)
        writer.write_enum_value("reason", self.reason)
        writer.write_additional_data_value(self.additional_data)
    

