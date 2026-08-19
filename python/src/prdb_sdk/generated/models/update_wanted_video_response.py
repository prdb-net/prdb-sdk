from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class UpdateWantedVideoResponse(AdditionalDataHolder, Parsable):
    """
    The updated wanted video entry.
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
    # Whether this wanted video has been fulfilled.
    is_fulfilled: Optional[bool] = None
    # When this wanted video entry was last updated.
    updated_at_utc: Optional[datetime.datetime] = None
    # ID of the video.
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdateWantedVideoResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdateWantedVideoResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UpdateWantedVideoResponse()
    
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
            "isFulfilled": lambda n : setattr(self, 'is_fulfilled', n.get_bool_value()),
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
        writer.write_datetime_value("fulfilledAtUtc", self.fulfilled_at_utc)
        writer.write_int_value("fulfilledInQuality", self.fulfilled_in_quality)
        writer.write_int_value("fulfillmentByApp", self.fulfillment_by_app)
        writer.write_str_value("fulfillmentExternalId", self.fulfillment_external_id)
        writer.write_bool_value("isFulfilled", self.is_fulfilled)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

