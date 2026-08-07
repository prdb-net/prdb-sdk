from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .favorite_actor_changes_cursor_dto import FavoriteActorChangesCursorDto
    from .get_favorite_actor_changes_response_next_cursor_member1 import GetFavoriteActorChangesResponse_nextCursorMember1

@dataclass
class GetFavoriteActorChangesResponse_nextCursor(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes FavoriteActorChangesCursorDto, GetFavoriteActorChangesResponse_nextCursorMember1
    """
    # Composed type representation for type FavoriteActorChangesCursorDto
    favorite_actor_changes_cursor_dto: Optional[FavoriteActorChangesCursorDto] = None
    # Composed type representation for type GetFavoriteActorChangesResponse_nextCursorMember1
    get_favorite_actor_changes_response_next_cursor_member1: Optional[GetFavoriteActorChangesResponse_nextCursorMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetFavoriteActorChangesResponse_nextCursor:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetFavoriteActorChangesResponse_nextCursor
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = GetFavoriteActorChangesResponse_nextCursor()
        if mapping_value and mapping_value.casefold() == "FavoriteActorChangesCursorDto".casefold():
            from .favorite_actor_changes_cursor_dto import FavoriteActorChangesCursorDto

            result.favorite_actor_changes_cursor_dto = FavoriteActorChangesCursorDto()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .favorite_actor_changes_cursor_dto import FavoriteActorChangesCursorDto
        from .get_favorite_actor_changes_response_next_cursor_member1 import GetFavoriteActorChangesResponse_nextCursorMember1

        if self.favorite_actor_changes_cursor_dto:
            return self.favorite_actor_changes_cursor_dto.get_field_deserializers()
        if self.get_favorite_actor_changes_response_next_cursor_member1:
            return self.get_favorite_actor_changes_response_next_cursor_member1.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.favorite_actor_changes_cursor_dto:
            writer.write_object_value(None, self.favorite_actor_changes_cursor_dto)
        elif self.get_favorite_actor_changes_response_next_cursor_member1:
            writer.write_object_value(None, self.get_favorite_actor_changes_response_next_cursor_member1)
    

