from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .video_filehash_change_filehash_dto import VideoFilehashChangeFilehashDto

@dataclass
class VideoFilehashChangeDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The eventType property
    event_type: Optional[str] = None
    # The filehash property
    filehash: Optional[VideoFilehashChangeFilehashDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoFilehashChangeDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoFilehashChangeDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoFilehashChangeDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_filehash_change_filehash_dto import VideoFilehashChangeFilehashDto

        from .video_filehash_change_filehash_dto import VideoFilehashChangeFilehashDto

        fields: dict[str, Callable[[Any], None]] = {
            "eventType": lambda n : setattr(self, 'event_type', n.get_str_value()),
            "filehash": lambda n : setattr(self, 'filehash', n.get_object_value(VideoFilehashChangeFilehashDto)),
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
        writer.write_str_value("eventType", self.event_type)
        writer.write_object_value("filehash", self.filehash)
        writer.write_additional_data_value(self.additional_data)
    

