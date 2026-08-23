from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class VideoCodecCountDto(AdditionalDataHolder, Parsable):
    """
    One video codec a video is known in, and how many of its files carry it.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Codec name as the probing client reported it, lower-cased ("h264", "hevc", "av1").
    codec: Optional[str] = None
    # How many of the video's files use this codec.
    file_count: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoCodecCountDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoCodecCountDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoCodecCountDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "codec": lambda n : setattr(self, 'codec', n.get_str_value()),
            "fileCount": lambda n : setattr(self, 'file_count', n.get_int_value()),
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
        writer.write_str_value("codec", self.codec)
        writer.write_int_value("fileCount", self.file_count)
        writer.write_additional_data_value(self.additional_data)
    

