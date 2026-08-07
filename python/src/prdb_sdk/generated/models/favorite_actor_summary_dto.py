from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class FavoriteActorSummaryDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ethnicity property
    ethnicity: Optional[str] = None
    # The favoritedAtUtc property
    favorited_at_utc: Optional[datetime.datetime] = None
    # The gender property
    gender: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # The name property
    name: Optional[str] = None
    # The nationality property
    nationality: Optional[str] = None
    # The profileImageCdnPath property
    profile_image_cdn_path: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FavoriteActorSummaryDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FavoriteActorSummaryDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FavoriteActorSummaryDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "ethnicity": lambda n : setattr(self, 'ethnicity', n.get_str_value()),
            "favoritedAtUtc": lambda n : setattr(self, 'favorited_at_utc', n.get_datetime_value()),
            "gender": lambda n : setattr(self, 'gender', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "nationality": lambda n : setattr(self, 'nationality', n.get_str_value()),
            "profileImageCdnPath": lambda n : setattr(self, 'profile_image_cdn_path', n.get_str_value()),
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
        writer.write_str_value("ethnicity", self.ethnicity)
        writer.write_datetime_value("favoritedAtUtc", self.favorited_at_utc)
        writer.write_str_value("gender", self.gender)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_str_value("nationality", self.nationality)
        writer.write_str_value("profileImageCdnPath", self.profile_image_cdn_path)
        writer.write_additional_data_value(self.additional_data)
    

