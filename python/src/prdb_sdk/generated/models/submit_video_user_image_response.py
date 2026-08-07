from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class SubmitVideoUserImageResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The moderationStatus property
    moderation_status: Optional[str] = None
    # The moderationTargetId property
    moderation_target_id: Optional[UUID] = None
    # The moderationVisibility property
    moderation_visibility: Optional[str] = None
    # The videoUserImageId property
    video_user_image_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SubmitVideoUserImageResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SubmitVideoUserImageResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SubmitVideoUserImageResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "moderationStatus": lambda n : setattr(self, 'moderation_status', n.get_str_value()),
            "moderationTargetId": lambda n : setattr(self, 'moderation_target_id', n.get_uuid_value()),
            "moderationVisibility": lambda n : setattr(self, 'moderation_visibility', n.get_str_value()),
            "videoUserImageId": lambda n : setattr(self, 'video_user_image_id', n.get_uuid_value()),
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
        writer.write_str_value("moderationStatus", self.moderation_status)
        writer.write_uuid_value("moderationTargetId", self.moderation_target_id)
        writer.write_str_value("moderationVisibility", self.moderation_visibility)
        writer.write_uuid_value("videoUserImageId", self.video_user_image_id)
        writer.write_additional_data_value(self.additional_data)
    

