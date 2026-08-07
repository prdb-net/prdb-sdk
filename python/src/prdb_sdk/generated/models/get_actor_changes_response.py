from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .actor_change_dto import ActorChangeDto

@dataclass
class GetActorChangesResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The hasMore property
    has_more: Optional[bool] = None
    # The items property
    items: Optional[list[ActorChangeDto]] = None
    # The nextCursorId property
    next_cursor_id: Optional[UUID] = None
    # The nextCursorUtc property
    next_cursor_utc: Optional[datetime.datetime] = None
    # The pageSize property
    page_size: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetActorChangesResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetActorChangesResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetActorChangesResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .actor_change_dto import ActorChangeDto

        from .actor_change_dto import ActorChangeDto

        fields: dict[str, Callable[[Any], None]] = {
            "hasMore": lambda n : setattr(self, 'has_more', n.get_bool_value()),
            "items": lambda n : setattr(self, 'items', n.get_collection_of_object_values(ActorChangeDto)),
            "nextCursorId": lambda n : setattr(self, 'next_cursor_id', n.get_uuid_value()),
            "nextCursorUtc": lambda n : setattr(self, 'next_cursor_utc', n.get_datetime_value()),
            "pageSize": lambda n : setattr(self, 'page_size', n.get_int_value()),
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
        writer.write_uuid_value("nextCursorId", self.next_cursor_id)
        writer.write_datetime_value("nextCursorUtc", self.next_cursor_utc)
        writer.write_int_value("pageSize", self.page_size)
        writer.write_additional_data_value(self.additional_data)
    

