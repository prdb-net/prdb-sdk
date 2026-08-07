from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .video_summary_actor_dto import VideoSummaryActorDto

@dataclass
class VideoSummaryDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The actors property
    actors: Optional[list[VideoSummaryActorDto]] = None
    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The id property
    id: Optional[UUID] = None
    # The releaseDate property
    release_date: Optional[datetime.date] = None
    # The siteId property
    site_id: Optional[UUID] = None
    # The siteTitle property
    site_title: Optional[str] = None
    # The title property
    title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoSummaryDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoSummaryDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoSummaryDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_summary_actor_dto import VideoSummaryActorDto

        from .video_summary_actor_dto import VideoSummaryActorDto

        fields: dict[str, Callable[[Any], None]] = {
            "actors": lambda n : setattr(self, 'actors', n.get_collection_of_object_values(VideoSummaryActorDto)),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "releaseDate": lambda n : setattr(self, 'release_date', n.get_date_value()),
            "siteId": lambda n : setattr(self, 'site_id', n.get_uuid_value()),
            "siteTitle": lambda n : setattr(self, 'site_title', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
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
        writer.write_collection_of_object_values("actors", self.actors)
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_uuid_value("id", self.id)
        writer.write_date_value("releaseDate", self.release_date)
        writer.write_uuid_value("siteId", self.site_id)
        writer.write_str_value("siteTitle", self.site_title)
        writer.write_str_value("title", self.title)
        writer.write_additional_data_value(self.additional_data)
    

