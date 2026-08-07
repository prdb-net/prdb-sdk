from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class ActorSummaryDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The birthday property
    birthday: Optional[datetime.date] = None
    # The ethnicity property
    ethnicity: Optional[int] = None
    # The ethnicityLabel property
    ethnicity_label: Optional[str] = None
    # The gender property
    gender: Optional[int] = None
    # The genderLabel property
    gender_label: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # The name property
    name: Optional[str] = None
    # The nationality property
    nationality: Optional[int] = None
    # The nationalityLabel property
    nationality_label: Optional[str] = None
    # The profileImageUrl property
    profile_image_url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ActorSummaryDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ActorSummaryDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ActorSummaryDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "birthday": lambda n : setattr(self, 'birthday', n.get_date_value()),
            "ethnicity": lambda n : setattr(self, 'ethnicity', n.get_int_value()),
            "ethnicityLabel": lambda n : setattr(self, 'ethnicity_label', n.get_str_value()),
            "gender": lambda n : setattr(self, 'gender', n.get_int_value()),
            "genderLabel": lambda n : setattr(self, 'gender_label', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "nationality": lambda n : setattr(self, 'nationality', n.get_int_value()),
            "nationalityLabel": lambda n : setattr(self, 'nationality_label', n.get_str_value()),
            "profileImageUrl": lambda n : setattr(self, 'profile_image_url', n.get_str_value()),
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
        writer.write_date_value("birthday", self.birthday)
        writer.write_int_value("ethnicity", self.ethnicity)
        writer.write_str_value("ethnicityLabel", self.ethnicity_label)
        writer.write_int_value("gender", self.gender)
        writer.write_str_value("genderLabel", self.gender_label)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_int_value("nationality", self.nationality)
        writer.write_str_value("nationalityLabel", self.nationality_label)
        writer.write_str_value("profileImageUrl", self.profile_image_url)
        writer.write_additional_data_value(self.additional_data)
    

