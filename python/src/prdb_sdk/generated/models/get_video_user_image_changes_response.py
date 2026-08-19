from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .video_user_image_changes_cursor_dto import VideoUserImageChangesCursorDto
    from .video_user_image_change_item_dto import VideoUserImageChangeItemDto

@dataclass
class GetVideoUserImageChangesResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The hasMore property
    has_more: Optional[bool] = None
    # The items property
    items: Optional[list[VideoUserImageChangeItemDto]] = None
    # The nextCursor property
    next_cursor: Optional[VideoUserImageChangesCursorDto] = None
    # The pageSize property
    page_size: Optional[int] = None
    # The server's clock when this page was produced, read before the rows were queried.Safe to persist as the next `since` when `items` is empty: an empty pagecarries no row timestamp to continue from, and a client's own clock or the HTTP`Date` header are not sound substitutes for a value the server later reads backas a lower bound.
    server_time_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetVideoUserImageChangesResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetVideoUserImageChangesResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetVideoUserImageChangesResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_user_image_changes_cursor_dto import VideoUserImageChangesCursorDto
        from .video_user_image_change_item_dto import VideoUserImageChangeItemDto

        from .video_user_image_changes_cursor_dto import VideoUserImageChangesCursorDto
        from .video_user_image_change_item_dto import VideoUserImageChangeItemDto

        fields: dict[str, Callable[[Any], None]] = {
            "hasMore": lambda n : setattr(self, 'has_more', n.get_bool_value()),
            "items": lambda n : setattr(self, 'items', n.get_collection_of_object_values(VideoUserImageChangeItemDto)),
            "nextCursor": lambda n : setattr(self, 'next_cursor', n.get_object_value(VideoUserImageChangesCursorDto)),
            "pageSize": lambda n : setattr(self, 'page_size', n.get_int_value()),
            "serverTimeUtc": lambda n : setattr(self, 'server_time_utc', n.get_datetime_value()),
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
        writer.write_bool_value("hasMore", self.has_more)
        writer.write_collection_of_object_values("items", self.items)
        writer.write_object_value("nextCursor", self.next_cursor)
        writer.write_int_value("pageSize", self.page_size)
        writer.write_datetime_value("serverTimeUtc", self.server_time_utc)
        writer.write_additional_data_value(self.additional_data)
    

