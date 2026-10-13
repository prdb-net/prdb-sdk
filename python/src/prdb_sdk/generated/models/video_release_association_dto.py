from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .video_release_association_dto_provider_key import VideoReleaseAssociationDto_providerKey

@dataclass
class VideoReleaseAssociationDto(AdditionalDataHolder, Parsable):
    """
    Metadata identity only. The central entry is not a file ID or a download capability.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The deletedAtUtc property
    deleted_at_utc: Optional[datetime.datetime] = None
    # The id property
    id: Optional[UUID] = None
    # False when evidence needs re-evaluation. Withhold automation and preserve unrelated/manual choices.
    is_confirmed: Optional[bool] = None
    # The isDeleted property
    is_deleted: Optional[bool] = None
    # The platformId property
    platform_id: Optional[UUID] = None
    # The platformKey property
    platform_key: Optional[str] = None
    # Allowed values: nzbcache.
    provider_key: Optional[VideoReleaseAssociationDto_providerKey] = None
    # The releaseName property
    release_name: Optional[str] = None
    # Entry UUID in the administratively verified shared central origin. Never infer a FileId from it.
    remote_entry_id: Optional[UUID] = None
    # The siteId property
    site_id: Optional[UUID] = None
    # Availability of the metadata source entry, independently of confirmation and actual file delivery.
    source_available: Optional[bool] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    # The videoId property
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoReleaseAssociationDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoReleaseAssociationDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoReleaseAssociationDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_release_association_dto_provider_key import VideoReleaseAssociationDto_providerKey

        from .video_release_association_dto_provider_key import VideoReleaseAssociationDto_providerKey

        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "deletedAtUtc": lambda n : setattr(self, 'deleted_at_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "isConfirmed": lambda n : setattr(self, 'is_confirmed', n.get_bool_value()),
            "isDeleted": lambda n : setattr(self, 'is_deleted', n.get_bool_value()),
            "platformId": lambda n : setattr(self, 'platform_id', n.get_uuid_value()),
            "platformKey": lambda n : setattr(self, 'platform_key', n.get_str_value()),
            "providerKey": lambda n : setattr(self, 'provider_key', n.get_enum_value(VideoReleaseAssociationDto_providerKey)),
            "releaseName": lambda n : setattr(self, 'release_name', n.get_str_value()),
            "remoteEntryId": lambda n : setattr(self, 'remote_entry_id', n.get_uuid_value()),
            "siteId": lambda n : setattr(self, 'site_id', n.get_uuid_value()),
            "sourceAvailable": lambda n : setattr(self, 'source_available', n.get_bool_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
            "videoId": lambda n : setattr(self, 'video_id', n.get_uuid_value()),
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
        writer.write_datetime_value("deletedAtUtc", self.deleted_at_utc)
        writer.write_uuid_value("id", self.id)
        writer.write_bool_value("isConfirmed", self.is_confirmed)
        writer.write_bool_value("isDeleted", self.is_deleted)
        writer.write_uuid_value("platformId", self.platform_id)
        writer.write_str_value("platformKey", self.platform_key)
        writer.write_enum_value("providerKey", self.provider_key)
        writer.write_str_value("releaseName", self.release_name)
        writer.write_uuid_value("remoteEntryId", self.remote_entry_id)
        writer.write_uuid_value("siteId", self.site_id)
        writer.write_bool_value("sourceAvailable", self.source_available)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

