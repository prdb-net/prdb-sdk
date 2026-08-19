from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID
from warnings import warn

@dataclass
class WantedVideoSummaryDto(AdditionalDataHolder, Parsable):
    """
    A wanted video entry for the current user.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # When this wanted video entry was created.
    created_at_utc: Optional[datetime.datetime] = None
    # When the wanted video was fulfilled, if applicable.
    fulfilled_at_utc: Optional[datetime.datetime] = None
    # Known values: P720 (0), P1080 (1), P2160 (2).
    fulfilled_in_quality: Optional[int] = None
    # Known values: Sabnzbd (0), Nzbget (1), Filesystem (2), Other (3), Ordeno (4).
    fulfillment_by_app: Optional[int] = None
    # External identifier from the fulfilling application, if applicable.
    fulfillment_external_id: Optional[str] = None
    # Deprecated alias for `imageUrl`, carrying the identical value. The name claimed apath fragment that was never sent; read `imageUrl` instead. Removed in the next majorversion.
    image_cdn_path: Optional[str] = None
    # Absolute URL for the video's primary image, if available: a complete URL including schemeand host, ready to request as-is.
    image_url: Optional[str] = None
    # Whether this wanted video has been fulfilled.
    is_fulfilled: Optional[bool] = None
    # Title of the site this video belongs to.
    site_title: Optional[str] = None
    # When this wanted video entry was last updated.
    updated_at_utc: Optional[datetime.datetime] = None
    # When the video was added to the database.
    video_created_at_utc: Optional[datetime.datetime] = None
    # ID of the wanted video.
    video_id: Optional[UUID] = None
    # Release date of the video, if known.
    video_release_date: Optional[datetime.date] = None
    # Video title.
    video_title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WantedVideoSummaryDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WantedVideoSummaryDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WantedVideoSummaryDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "fulfilledAtUtc": lambda n : setattr(self, 'fulfilled_at_utc', n.get_datetime_value()),
            "fulfilledInQuality": lambda n : setattr(self, 'fulfilled_in_quality', n.get_int_value()),
            "fulfillmentByApp": lambda n : setattr(self, 'fulfillment_by_app', n.get_int_value()),
            "fulfillmentExternalId": lambda n : setattr(self, 'fulfillment_external_id', n.get_str_value()),
            "imageCdnPath": lambda n : setattr(self, 'image_cdn_path', n.get_str_value()),
            "imageUrl": lambda n : setattr(self, 'image_url', n.get_str_value()),
            "isFulfilled": lambda n : setattr(self, 'is_fulfilled', n.get_bool_value()),
            "siteTitle": lambda n : setattr(self, 'site_title', n.get_str_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
            "videoCreatedAtUtc": lambda n : setattr(self, 'video_created_at_utc', n.get_datetime_value()),
            "videoId": lambda n : setattr(self, 'video_id', n.get_uuid_value()),
            "videoReleaseDate": lambda n : setattr(self, 'video_release_date', n.get_date_value()),
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
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_datetime_value("fulfilledAtUtc", self.fulfilled_at_utc)
        writer.write_int_value("fulfilledInQuality", self.fulfilled_in_quality)
        writer.write_int_value("fulfillmentByApp", self.fulfillment_by_app)
        writer.write_str_value("fulfillmentExternalId", self.fulfillment_external_id)
        writer.write_str_value("imageCdnPath", self.image_cdn_path)
        writer.write_str_value("imageUrl", self.image_url)
        writer.write_bool_value("isFulfilled", self.is_fulfilled)
        writer.write_str_value("siteTitle", self.site_title)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_datetime_value("videoCreatedAtUtc", self.video_created_at_utc)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_date_value("videoReleaseDate", self.video_release_date)
        writer.write_str_value("videoTitle", self.video_title)
        writer.write_additional_data_value(self.additional_data)
    

