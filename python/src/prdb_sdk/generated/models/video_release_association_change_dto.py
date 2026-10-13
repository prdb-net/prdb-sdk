from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .video_release_association_change_dto_event_type import VideoReleaseAssociationChangeDto_eventType
    from .video_release_association_dto import VideoReleaseAssociationDto

@dataclass
class VideoReleaseAssociationChangeDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Allowed values: created, updated, deleted.
    event_type: Optional[VideoReleaseAssociationChangeDto_eventType] = None
    # Metadata identity only. The central entry is not a file ID or a download capability.
    video_release_association: Optional[VideoReleaseAssociationDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoReleaseAssociationChangeDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoReleaseAssociationChangeDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoReleaseAssociationChangeDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_release_association_change_dto_event_type import VideoReleaseAssociationChangeDto_eventType
        from .video_release_association_dto import VideoReleaseAssociationDto

        from .video_release_association_change_dto_event_type import VideoReleaseAssociationChangeDto_eventType
        from .video_release_association_dto import VideoReleaseAssociationDto

        fields: dict[str, Callable[[Any], None]] = {
            "eventType": lambda n : setattr(self, 'event_type', n.get_enum_value(VideoReleaseAssociationChangeDto_eventType)),
            "videoReleaseAssociation": lambda n : setattr(self, 'video_release_association', n.get_object_value(VideoReleaseAssociationDto)),
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
        writer.write_enum_value("eventType", self.event_type)
        writer.write_object_value("videoReleaseAssociation", self.video_release_association)
        writer.write_additional_data_value(self.additional_data)
    

