from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .video_detail_actor_dto import VideoDetailActorDto
    from .video_detail_image_dto import VideoDetailImageDto
    from .video_detail_pre_name_dto import VideoDetailPreNameDto
    from .video_detail_site_dto import VideoDetailSiteDto

@dataclass
class VideoDetailDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The actors property
    actors: Optional[list[VideoDetailActorDto]] = None
    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The id property
    id: Optional[UUID] = None
    # Images for this video, ordered oldest first by the time they were added, with the image IDas the tie-breaker. The order is stable across requests.
    images: Optional[list[VideoDetailImageDto]] = None
    # The preNames property
    pre_names: Optional[list[VideoDetailPreNameDto]] = None
    # The releaseDate property
    release_date: Optional[datetime.date] = None
    # The site property
    site: Optional[VideoDetailSiteDto] = None
    # The title property
    title: Optional[str] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoDetailDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoDetailDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoDetailDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_detail_actor_dto import VideoDetailActorDto
        from .video_detail_image_dto import VideoDetailImageDto
        from .video_detail_pre_name_dto import VideoDetailPreNameDto
        from .video_detail_site_dto import VideoDetailSiteDto

        from .video_detail_actor_dto import VideoDetailActorDto
        from .video_detail_image_dto import VideoDetailImageDto
        from .video_detail_pre_name_dto import VideoDetailPreNameDto
        from .video_detail_site_dto import VideoDetailSiteDto

        fields: dict[str, Callable[[Any], None]] = {
            "actors": lambda n : setattr(self, 'actors', n.get_collection_of_object_values(VideoDetailActorDto)),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "images": lambda n : setattr(self, 'images', n.get_collection_of_object_values(VideoDetailImageDto)),
            "preNames": lambda n : setattr(self, 'pre_names', n.get_collection_of_object_values(VideoDetailPreNameDto)),
            "releaseDate": lambda n : setattr(self, 'release_date', n.get_date_value()),
            "site": lambda n : setattr(self, 'site', n.get_object_value(VideoDetailSiteDto)),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
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
        writer.write_collection_of_object_values("images", self.images)
        writer.write_collection_of_object_values("preNames", self.pre_names)
        writer.write_date_value("releaseDate", self.release_date)
        writer.write_object_value("site", self.site)
        writer.write_str_value("title", self.title)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_additional_data_value(self.additional_data)
    

