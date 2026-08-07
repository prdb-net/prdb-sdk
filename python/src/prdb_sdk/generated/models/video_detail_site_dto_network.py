from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .video_detail_network_dto import VideoDetailNetworkDto
    from .video_detail_site_dto_network_member1 import VideoDetailSiteDto_networkMember1

@dataclass
class VideoDetailSiteDto_network(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes VideoDetailNetworkDto, VideoDetailSiteDto_networkMember1
    """
    # Composed type representation for type VideoDetailNetworkDto
    video_detail_network_dto: Optional[VideoDetailNetworkDto] = None
    # Composed type representation for type VideoDetailSiteDto_networkMember1
    video_detail_site_dto_network_member1: Optional[VideoDetailSiteDto_networkMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoDetailSiteDto_network:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoDetailSiteDto_network
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = VideoDetailSiteDto_network()
        if mapping_value and mapping_value.casefold() == "VideoDetailNetworkDto".casefold():
            from .video_detail_network_dto import VideoDetailNetworkDto

            result.video_detail_network_dto = VideoDetailNetworkDto()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_detail_network_dto import VideoDetailNetworkDto
        from .video_detail_site_dto_network_member1 import VideoDetailSiteDto_networkMember1

        if self.video_detail_network_dto:
            return self.video_detail_network_dto.get_field_deserializers()
        if self.video_detail_site_dto_network_member1:
            return self.video_detail_site_dto_network_member1.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.video_detail_network_dto:
            writer.write_object_value(None, self.video_detail_network_dto)
        elif self.video_detail_site_dto_network_member1:
            writer.write_object_value(None, self.video_detail_site_dto_network_member1)
    

