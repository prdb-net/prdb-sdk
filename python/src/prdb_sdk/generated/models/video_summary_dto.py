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
    """
    Summary of a single video.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Actors appearing in this video.
    actors: Optional[list[VideoSummaryActorDto]] = None
    # Timestamp when the video was created in PRDB.
    created_at_utc: Optional[datetime.datetime] = None
    # How many files the duration was taken over, without which the spread cannot be read.
    duration_file_count: Optional[int] = None
    # Consensus duration in milliseconds across the files prdb holds for this video, or null whiletoo few independent submitters have reported one. A median over the video's files, so atrailer submitted under the same video does not move it.
    duration_ms: Optional[int] = None
    # How far those files disagree about the duration, in milliseconds (median absolutedeviation). Zero means they agree; a large value means several versions are in circulation.
    duration_spread_ms: Optional[int] = None
    # Unique identifier of the video.
    id: Optional[UUID] = None
    # Release date of the video, if known.
    release_date: Optional[datetime.date] = None
    # Unique identifier of the site this video belongs to.
    site_id: Optional[UUID] = None
    # Title of the site this video belongs to.
    site_title: Optional[str] = None
    # Video title.
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
            "durationFileCount": lambda n : setattr(self, 'duration_file_count', n.get_int_value()),
            "durationMs": lambda n : setattr(self, 'duration_ms', n.get_int_value()),
            "durationSpreadMs": lambda n : setattr(self, 'duration_spread_ms', n.get_int_value()),
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
        writer.write_int_value("durationFileCount", self.duration_file_count)
        writer.write_int_value("durationMs", self.duration_ms)
        writer.write_int_value("durationSpreadMs", self.duration_spread_ms)
        writer.write_uuid_value("id", self.id)
        writer.write_date_value("releaseDate", self.release_date)
        writer.write_uuid_value("siteId", self.site_id)
        writer.write_str_value("siteTitle", self.site_title)
        writer.write_str_value("title", self.title)
        writer.write_additional_data_value(self.additional_data)
    

