from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .actor_change_alias_dto import ActorChangeAliasDto
    from .actor_change_bio_dto import ActorChangeBioDto
    from .actor_change_image_dto import ActorChangeImageDto
    from .actor_change_link_dto import ActorChangeLinkDto

@dataclass
class ActorChangeActorDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The aliases property
    aliases: Optional[list[ActorChangeAliasDto]] = None
    # The bios property
    bios: Optional[list[ActorChangeBioDto]] = None
    # The birthday property
    birthday: Optional[datetime.date] = None
    # The birthdayType property
    birthday_type: Optional[int] = None
    # The birthdayTypeLabel property
    birthday_type_label: Optional[str] = None
    # The birthplace property
    birthplace: Optional[str] = None
    # The braSize property
    bra_size: Optional[int] = None
    # The braSizeLabel property
    bra_size_label: Optional[str] = None
    # The breastType property
    breast_type: Optional[int] = None
    # The breastTypeLabel property
    breast_type_label: Optional[str] = None
    # The careerEnd property
    career_end: Optional[int] = None
    # The careerStart property
    career_start: Optional[int] = None
    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The deathday property
    deathday: Optional[datetime.date] = None
    # The deletedAtUtc property
    deleted_at_utc: Optional[datetime.datetime] = None
    # The ethnicity property
    ethnicity: Optional[int] = None
    # The ethnicityLabel property
    ethnicity_label: Optional[str] = None
    # The eyecolor property
    eyecolor: Optional[int] = None
    # The eyecolorLabel property
    eyecolor_label: Optional[str] = None
    # The gender property
    gender: Optional[int] = None
    # The genderLabel property
    gender_label: Optional[str] = None
    # The haircolor property
    haircolor: Optional[int] = None
    # The haircolorLabel property
    haircolor_label: Optional[str] = None
    # The height property
    height: Optional[int] = None
    # The hipSize property
    hip_size: Optional[int] = None
    # The id property
    id: Optional[UUID] = None
    # The images property
    images: Optional[list[ActorChangeImageDto]] = None
    # The isDeleted property
    is_deleted: Optional[bool] = None
    # The links property
    links: Optional[list[ActorChangeLinkDto]] = None
    # The name property
    name: Optional[str] = None
    # The nationality property
    nationality: Optional[int] = None
    # The nationalityLabel property
    nationality_label: Optional[str] = None
    # The piercings property
    piercings: Optional[str] = None
    # The tattoos property
    tattoos: Optional[str] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    # The waistSize property
    waist_size: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ActorChangeActorDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ActorChangeActorDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ActorChangeActorDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .actor_change_alias_dto import ActorChangeAliasDto
        from .actor_change_bio_dto import ActorChangeBioDto
        from .actor_change_image_dto import ActorChangeImageDto
        from .actor_change_link_dto import ActorChangeLinkDto

        from .actor_change_alias_dto import ActorChangeAliasDto
        from .actor_change_bio_dto import ActorChangeBioDto
        from .actor_change_image_dto import ActorChangeImageDto
        from .actor_change_link_dto import ActorChangeLinkDto

        fields: dict[str, Callable[[Any], None]] = {
            "aliases": lambda n : setattr(self, 'aliases', n.get_collection_of_object_values(ActorChangeAliasDto)),
            "bios": lambda n : setattr(self, 'bios', n.get_collection_of_object_values(ActorChangeBioDto)),
            "birthday": lambda n : setattr(self, 'birthday', n.get_date_value()),
            "birthdayType": lambda n : setattr(self, 'birthday_type', n.get_int_value()),
            "birthdayTypeLabel": lambda n : setattr(self, 'birthday_type_label', n.get_str_value()),
            "birthplace": lambda n : setattr(self, 'birthplace', n.get_str_value()),
            "braSize": lambda n : setattr(self, 'bra_size', n.get_int_value()),
            "braSizeLabel": lambda n : setattr(self, 'bra_size_label', n.get_str_value()),
            "breastType": lambda n : setattr(self, 'breast_type', n.get_int_value()),
            "breastTypeLabel": lambda n : setattr(self, 'breast_type_label', n.get_str_value()),
            "careerEnd": lambda n : setattr(self, 'career_end', n.get_int_value()),
            "careerStart": lambda n : setattr(self, 'career_start', n.get_int_value()),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "deathday": lambda n : setattr(self, 'deathday', n.get_date_value()),
            "deletedAtUtc": lambda n : setattr(self, 'deleted_at_utc', n.get_datetime_value()),
            "ethnicity": lambda n : setattr(self, 'ethnicity', n.get_int_value()),
            "ethnicityLabel": lambda n : setattr(self, 'ethnicity_label', n.get_str_value()),
            "eyecolor": lambda n : setattr(self, 'eyecolor', n.get_int_value()),
            "eyecolorLabel": lambda n : setattr(self, 'eyecolor_label', n.get_str_value()),
            "gender": lambda n : setattr(self, 'gender', n.get_int_value()),
            "genderLabel": lambda n : setattr(self, 'gender_label', n.get_str_value()),
            "haircolor": lambda n : setattr(self, 'haircolor', n.get_int_value()),
            "haircolorLabel": lambda n : setattr(self, 'haircolor_label', n.get_str_value()),
            "height": lambda n : setattr(self, 'height', n.get_int_value()),
            "hipSize": lambda n : setattr(self, 'hip_size', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "images": lambda n : setattr(self, 'images', n.get_collection_of_object_values(ActorChangeImageDto)),
            "isDeleted": lambda n : setattr(self, 'is_deleted', n.get_bool_value()),
            "links": lambda n : setattr(self, 'links', n.get_collection_of_object_values(ActorChangeLinkDto)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "nationality": lambda n : setattr(self, 'nationality', n.get_int_value()),
            "nationalityLabel": lambda n : setattr(self, 'nationality_label', n.get_str_value()),
            "piercings": lambda n : setattr(self, 'piercings', n.get_str_value()),
            "tattoos": lambda n : setattr(self, 'tattoos', n.get_str_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
            "waistSize": lambda n : setattr(self, 'waist_size', n.get_int_value()),
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
        writer.write_collection_of_object_values("aliases", self.aliases)
        writer.write_collection_of_object_values("bios", self.bios)
        writer.write_date_value("birthday", self.birthday)
        writer.write_int_value("birthdayType", self.birthday_type)
        writer.write_str_value("birthdayTypeLabel", self.birthday_type_label)
        writer.write_str_value("birthplace", self.birthplace)
        writer.write_int_value("braSize", self.bra_size)
        writer.write_str_value("braSizeLabel", self.bra_size_label)
        writer.write_int_value("breastType", self.breast_type)
        writer.write_str_value("breastTypeLabel", self.breast_type_label)
        writer.write_int_value("careerEnd", self.career_end)
        writer.write_int_value("careerStart", self.career_start)
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_date_value("deathday", self.deathday)
        writer.write_datetime_value("deletedAtUtc", self.deleted_at_utc)
        writer.write_int_value("ethnicity", self.ethnicity)
        writer.write_str_value("ethnicityLabel", self.ethnicity_label)
        writer.write_int_value("eyecolor", self.eyecolor)
        writer.write_str_value("eyecolorLabel", self.eyecolor_label)
        writer.write_int_value("gender", self.gender)
        writer.write_str_value("genderLabel", self.gender_label)
        writer.write_int_value("haircolor", self.haircolor)
        writer.write_str_value("haircolorLabel", self.haircolor_label)
        writer.write_int_value("height", self.height)
        writer.write_int_value("hipSize", self.hip_size)
        writer.write_uuid_value("id", self.id)
        writer.write_collection_of_object_values("images", self.images)
        writer.write_bool_value("isDeleted", self.is_deleted)
        writer.write_collection_of_object_values("links", self.links)
        writer.write_str_value("name", self.name)
        writer.write_int_value("nationality", self.nationality)
        writer.write_str_value("nationalityLabel", self.nationality_label)
        writer.write_str_value("piercings", self.piercings)
        writer.write_str_value("tattoos", self.tattoos)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_int_value("waistSize", self.waist_size)
        writer.write_additional_data_value(self.additional_data)
    

