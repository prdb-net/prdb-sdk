from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .video_change_actor_dto import VideoChangeActorDto
    from .video_change_image_dto import VideoChangeImageDto
    from .video_change_pre_name_dto import VideoChangePreNameDto
    from .video_change_site_dto import VideoChangeSiteDto
    from .video_quality_overview_dto import VideoQualityOverviewDto

@dataclass
class VideoChangeVideoDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The actors property
    actors: Optional[list[VideoChangeActorDto]] = None
    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The deletedAtUtc property
    deleted_at_utc: Optional[datetime.datetime] = None
    # Catalogue description of the video, if known.
    description: Optional[str] = None
    # How many files the duration was taken over. The spread cannot be read without it — one overtwo files says far less than one over twenty. Null exactly when `durationMs` is null.
    duration_file_count: Optional[int] = None
    # Consensus duration in milliseconds across the files prdb holds for this video, or null whiletoo few independent submitters have reported one. A median, not an average: durations differlegitimately — cuts, with and without an intro, re-encodes with padding — and one shortoutlier would drag an average off the value the real files agree on.
    duration_ms: Optional[int] = None
    # How far the files disagree about the duration, in milliseconds (median absolute deviation).Zero means every file agrees; a large value means several versions are in circulation, whichis the more useful of the two statements. Null exactly when `durationMs` is null.
    duration_spread_ms: Optional[int] = None
    # The id property
    id: Optional[UUID] = None
    # Images for this video, ordered oldest first by the time they were added, with the image IDas the tie-breaker. The order is stable across requests.
    images: Optional[list[VideoChangeImageDto]] = None
    # The isDeleted property
    is_deleted: Optional[bool] = None
    # Surviving video UUID when deleted by a merge; otherwise null.
    merged_into_id: Optional[UUID] = None
    # The preNames property
    pre_names: Optional[list[VideoChangePreNameDto]] = None
    # What technical shapes a video is known to exist in, counted over the files prdb holds for it.
    quality_overview: Optional[VideoQualityOverviewDto] = None
    # The releaseDate property
    release_date: Optional[datetime.date] = None
    # The site property
    site: Optional[VideoChangeSiteDto] = None
    # StashDB Scene UUID for a confirmed match. This is only an external identity: prdb does notexpose match evidence or proxy StashDB, and clients use their own credentials to resolve it.
    stashdb_scene_id: Optional[UUID] = None
    # The title property
    title: Optional[str] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoChangeVideoDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoChangeVideoDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoChangeVideoDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_change_actor_dto import VideoChangeActorDto
        from .video_change_image_dto import VideoChangeImageDto
        from .video_change_pre_name_dto import VideoChangePreNameDto
        from .video_change_site_dto import VideoChangeSiteDto
        from .video_quality_overview_dto import VideoQualityOverviewDto

        from .video_change_actor_dto import VideoChangeActorDto
        from .video_change_image_dto import VideoChangeImageDto
        from .video_change_pre_name_dto import VideoChangePreNameDto
        from .video_change_site_dto import VideoChangeSiteDto
        from .video_quality_overview_dto import VideoQualityOverviewDto

        fields: dict[str, Callable[[Any], None]] = {
            "actors": lambda n : setattr(self, 'actors', n.get_collection_of_object_values(VideoChangeActorDto)),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "deletedAtUtc": lambda n : setattr(self, 'deleted_at_utc', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "durationFileCount": lambda n : setattr(self, 'duration_file_count', n.get_int_value()),
            "durationMs": lambda n : setattr(self, 'duration_ms', n.get_int_value()),
            "durationSpreadMs": lambda n : setattr(self, 'duration_spread_ms', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "images": lambda n : setattr(self, 'images', n.get_collection_of_object_values(VideoChangeImageDto)),
            "isDeleted": lambda n : setattr(self, 'is_deleted', n.get_bool_value()),
            "mergedIntoId": lambda n : setattr(self, 'merged_into_id', n.get_uuid_value()),
            "preNames": lambda n : setattr(self, 'pre_names', n.get_collection_of_object_values(VideoChangePreNameDto)),
            "qualityOverview": lambda n : setattr(self, 'quality_overview', n.get_object_value(VideoQualityOverviewDto)),
            "releaseDate": lambda n : setattr(self, 'release_date', n.get_date_value()),
            "site": lambda n : setattr(self, 'site', n.get_object_value(VideoChangeSiteDto)),
            "stashdbSceneId": lambda n : setattr(self, 'stashdb_scene_id', n.get_uuid_value()),
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
        writer.write_datetime_value("deletedAtUtc", self.deleted_at_utc)
        writer.write_str_value("description", self.description)
        writer.write_int_value("durationFileCount", self.duration_file_count)
        writer.write_int_value("durationMs", self.duration_ms)
        writer.write_int_value("durationSpreadMs", self.duration_spread_ms)
        writer.write_uuid_value("id", self.id)
        writer.write_collection_of_object_values("images", self.images)
        writer.write_bool_value("isDeleted", self.is_deleted)
        writer.write_uuid_value("mergedIntoId", self.merged_into_id)
        writer.write_collection_of_object_values("preNames", self.pre_names)
        writer.write_object_value("qualityOverview", self.quality_overview)
        writer.write_date_value("releaseDate", self.release_date)
        writer.write_object_value("site", self.site)
        writer.write_uuid_value("stashdbSceneId", self.stashdb_scene_id)
        writer.write_str_value("title", self.title)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_additional_data_value(self.additional_data)
    

