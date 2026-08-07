from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_video_filehash_changes_response_next_cursor_member1 import GetVideoFilehashChangesResponse_nextCursorMember1
    from .video_filehash_changes_cursor_dto import VideoFilehashChangesCursorDto

@dataclass
class GetVideoFilehashChangesResponse_nextCursor(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes GetVideoFilehashChangesResponse_nextCursorMember1, VideoFilehashChangesCursorDto
    """
    # Composed type representation for type GetVideoFilehashChangesResponse_nextCursorMember1
    get_video_filehash_changes_response_next_cursor_member1: Optional[GetVideoFilehashChangesResponse_nextCursorMember1] = None
    # Composed type representation for type VideoFilehashChangesCursorDto
    video_filehash_changes_cursor_dto: Optional[VideoFilehashChangesCursorDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetVideoFilehashChangesResponse_nextCursor:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetVideoFilehashChangesResponse_nextCursor
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = GetVideoFilehashChangesResponse_nextCursor()
        if mapping_value and mapping_value.casefold() == "VideoFilehashChangesCursorDto".casefold():
            from .video_filehash_changes_cursor_dto import VideoFilehashChangesCursorDto

            result.video_filehash_changes_cursor_dto = VideoFilehashChangesCursorDto()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .get_video_filehash_changes_response_next_cursor_member1 import GetVideoFilehashChangesResponse_nextCursorMember1
        from .video_filehash_changes_cursor_dto import VideoFilehashChangesCursorDto

        if self.get_video_filehash_changes_response_next_cursor_member1:
            return self.get_video_filehash_changes_response_next_cursor_member1.get_field_deserializers()
        if self.video_filehash_changes_cursor_dto:
            return self.video_filehash_changes_cursor_dto.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.get_video_filehash_changes_response_next_cursor_member1:
            writer.write_object_value(None, self.get_video_filehash_changes_response_next_cursor_member1)
        elif self.video_filehash_changes_cursor_dto:
            writer.write_object_value(None, self.video_filehash_changes_cursor_dto)
    

