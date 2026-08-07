from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .latest_pre_db_item_dto_video_member1 import LatestPreDbItemDto_videoMember1
    from .latest_pre_db_video_dto import LatestPreDbVideoDto

@dataclass
class LatestPreDbItemDto_video(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes LatestPreDbItemDto_videoMember1, LatestPreDbVideoDto
    """
    # Composed type representation for type LatestPreDbItemDto_videoMember1
    latest_pre_db_item_dto_video_member1: Optional[LatestPreDbItemDto_videoMember1] = None
    # Composed type representation for type LatestPreDbVideoDto
    latest_pre_db_video_dto: Optional[LatestPreDbVideoDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> LatestPreDbItemDto_video:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: LatestPreDbItemDto_video
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = LatestPreDbItemDto_video()
        if mapping_value and mapping_value.casefold() == "LatestPreDbVideoDto".casefold():
            from .latest_pre_db_video_dto import LatestPreDbVideoDto

            result.latest_pre_db_video_dto = LatestPreDbVideoDto()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .latest_pre_db_item_dto_video_member1 import LatestPreDbItemDto_videoMember1
        from .latest_pre_db_video_dto import LatestPreDbVideoDto

        if self.latest_pre_db_item_dto_video_member1:
            return self.latest_pre_db_item_dto_video_member1.get_field_deserializers()
        if self.latest_pre_db_video_dto:
            return self.latest_pre_db_video_dto.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.latest_pre_db_item_dto_video_member1:
            writer.write_object_value(None, self.latest_pre_db_item_dto_video_member1)
        elif self.latest_pre_db_video_dto:
            writer.write_object_value(None, self.latest_pre_db_video_dto)
    

