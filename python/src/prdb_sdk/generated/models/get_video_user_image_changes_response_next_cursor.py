from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_video_user_image_changes_response_next_cursor_member1 import GetVideoUserImageChangesResponse_nextCursorMember1
    from .video_user_image_changes_cursor_dto import VideoUserImageChangesCursorDto

@dataclass
class GetVideoUserImageChangesResponse_nextCursor(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes GetVideoUserImageChangesResponse_nextCursorMember1, VideoUserImageChangesCursorDto
    """
    # Composed type representation for type GetVideoUserImageChangesResponse_nextCursorMember1
    get_video_user_image_changes_response_next_cursor_member1: Optional[GetVideoUserImageChangesResponse_nextCursorMember1] = None
    # Composed type representation for type VideoUserImageChangesCursorDto
    video_user_image_changes_cursor_dto: Optional[VideoUserImageChangesCursorDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetVideoUserImageChangesResponse_nextCursor:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetVideoUserImageChangesResponse_nextCursor
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = GetVideoUserImageChangesResponse_nextCursor()
        if mapping_value and mapping_value.casefold() == "VideoUserImageChangesCursorDto".casefold():
            from .video_user_image_changes_cursor_dto import VideoUserImageChangesCursorDto

            result.video_user_image_changes_cursor_dto = VideoUserImageChangesCursorDto()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .get_video_user_image_changes_response_next_cursor_member1 import GetVideoUserImageChangesResponse_nextCursorMember1
        from .video_user_image_changes_cursor_dto import VideoUserImageChangesCursorDto

        if self.get_video_user_image_changes_response_next_cursor_member1:
            return self.get_video_user_image_changes_response_next_cursor_member1.get_field_deserializers()
        if self.video_user_image_changes_cursor_dto:
            return self.video_user_image_changes_cursor_dto.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.get_video_user_image_changes_response_next_cursor_member1:
            writer.write_object_value(None, self.get_video_user_image_changes_response_next_cursor_member1)
        elif self.video_user_image_changes_cursor_dto:
            writer.write_object_value(None, self.video_user_image_changes_cursor_dto)
    

