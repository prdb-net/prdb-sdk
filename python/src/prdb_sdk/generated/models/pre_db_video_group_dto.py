from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .pre_db_item_dto import PreDbItemDto

@dataclass
class PreDbVideoGroupDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The predbs property
    predbs: Optional[list[PreDbItemDto]] = None
    # The siteId property
    site_id: Optional[UUID] = None
    # The siteTitle property
    site_title: Optional[str] = None
    # The videoId property
    video_id: Optional[UUID] = None
    # The videoTitle property
    video_title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PreDbVideoGroupDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PreDbVideoGroupDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PreDbVideoGroupDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .pre_db_item_dto import PreDbItemDto

        from .pre_db_item_dto import PreDbItemDto

        fields: dict[str, Callable[[Any], None]] = {
            "predbs": lambda n : setattr(self, 'predbs', n.get_collection_of_object_values(PreDbItemDto)),
            "siteId": lambda n : setattr(self, 'site_id', n.get_uuid_value()),
            "siteTitle": lambda n : setattr(self, 'site_title', n.get_str_value()),
            "videoId": lambda n : setattr(self, 'video_id', n.get_uuid_value()),
            "videoTitle": lambda n : setattr(self, 'video_title', n.get_str_value()),
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
        writer.write_collection_of_object_values("predbs", self.predbs)
        writer.write_uuid_value("siteId", self.site_id)
        writer.write_str_value("siteTitle", self.site_title)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_str_value("videoTitle", self.video_title)
        writer.write_additional_data_value(self.additional_data)
    

