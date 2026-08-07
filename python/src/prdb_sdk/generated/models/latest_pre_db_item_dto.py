from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .latest_pre_db_item_dto_video import LatestPreDbItemDto_video

@dataclass
class LatestPreDbItemDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The id property
    id: Optional[UUID] = None
    # The title property
    title: Optional[str] = None
    # The video property
    video: Optional[LatestPreDbItemDto_video] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> LatestPreDbItemDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: LatestPreDbItemDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return LatestPreDbItemDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .latest_pre_db_item_dto_video import LatestPreDbItemDto_video

        from .latest_pre_db_item_dto_video import LatestPreDbItemDto_video

        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "video": lambda n : setattr(self, 'video', n.get_object_value(LatestPreDbItemDto_video)),
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
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("title", self.title)
        writer.write_object_value("video", self.video)
        writer.write_additional_data_value(self.additional_data)
    

