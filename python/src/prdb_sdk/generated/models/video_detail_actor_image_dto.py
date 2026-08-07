from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class VideoDetailActorImageDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The cdnPath property
    cdn_path: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # Known values: Thumbnail (1), Poster (2), Face (3).
    image_type: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoDetailActorImageDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoDetailActorImageDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoDetailActorImageDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "cdnPath": lambda n : setattr(self, 'cdn_path', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "imageType": lambda n : setattr(self, 'image_type', n.get_int_value()),
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
        writer.write_str_value("cdnPath", self.cdn_path)
        writer.write_uuid_value("id", self.id)
        writer.write_int_value("imageType", self.image_type)
        writer.write_additional_data_value(self.additional_data)
    

