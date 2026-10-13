from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class ResolvedReleaseVideo(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # False means missing actors cannot be treated as evidence of absence.
    actor_credits_complete: Optional[bool] = None
    # The actorIds property
    actor_ids: Optional[list[UUID]] = None
    # The catalogueUpdatedAtUtc property
    catalogue_updated_at_utc: Optional[datetime.datetime] = None
    # The releaseDate property
    release_date: Optional[datetime.date] = None
    # The siteId property
    site_id: Optional[UUID] = None
    # The videoId property
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResolvedReleaseVideo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResolvedReleaseVideo
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResolvedReleaseVideo()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "actorCreditsComplete": lambda n : setattr(self, 'actor_credits_complete', n.get_bool_value()),
            "actorIds": lambda n : setattr(self, 'actor_ids', n.get_collection_of_primitive_values(UUID)),
            "catalogueUpdatedAtUtc": lambda n : setattr(self, 'catalogue_updated_at_utc', n.get_datetime_value()),
            "releaseDate": lambda n : setattr(self, 'release_date', n.get_date_value()),
            "siteId": lambda n : setattr(self, 'site_id', n.get_uuid_value()),
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
        writer.write_bool_value("actorCreditsComplete", self.actor_credits_complete)
        writer.write_collection_of_primitive_values("actorIds", self.actor_ids)
        writer.write_datetime_value("catalogueUpdatedAtUtc", self.catalogue_updated_at_utc)
        writer.write_date_value("releaseDate", self.release_date)
        writer.write_uuid_value("siteId", self.site_id)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

