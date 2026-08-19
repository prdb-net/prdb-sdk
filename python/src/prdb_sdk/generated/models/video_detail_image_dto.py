from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID
from warnings import warn

@dataclass
class VideoDetailImageDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Deprecated alias for `url`, carrying the identical value. The name claimed a pathfragment that was never sent; read `url` instead. Removed in the next major version.
    cdn_path: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # Absolute URL for the image, if available: a complete URL including scheme and host, ready torequest as-is. This is the same value the deprecated `cdnPath` carries.
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoDetailImageDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoDetailImageDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoDetailImageDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "cdnPath": lambda n : setattr(self, 'cdn_path', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "url": lambda n : setattr(self, 'url', n.get_str_value()),
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
        writer.write_str_value("url", self.url)
        writer.write_additional_data_value(self.additional_data)
    

