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
    """
    Full current actor payload, including tombstone metadata.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The aliases property
    aliases: Optional[list[ActorChangeAliasDto]] = None
    # The bios property
    bios: Optional[list[ActorChangeBioDto]] = None
    # The birthday property
    birthday: Optional[datetime.date] = None
    # Known values: ExactDate (1), MonthYear (2), Year (3).
    birthday_type: Optional[int] = None
    # The birthdayTypeLabel property
    birthday_type_label: Optional[str] = None
    # The birthplace property
    birthplace: Optional[str] = None
    # The braSize property
    bra_size: Optional[int] = None
    # The braSizeLabel property
    bra_size_label: Optional[str] = None
    # Known values: Unknown (0), Natural (1), Augmented (2), NotApplicable (3).
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
    # Known values: Unknown (0), Caucasian (1), Black (2), Asian (3), Indian (4), Latin (5), MiddleEastern (6), Mixed (7), Other (8).
    ethnicity: Optional[int] = None
    # The ethnicityLabel property
    ethnicity_label: Optional[str] = None
    # Known values: Unknown (0), Blue (1), Brown (2), Grey (3), Red (4), Green (5), Hazel (6).
    eyecolor: Optional[int] = None
    # The eyecolorLabel property
    eyecolor_label: Optional[str] = None
    # Known values: Unknown (0), Female (1), Male (2), Intersex (3), Transmale (4), Transfemale (5), NonBinary (6).
    gender: Optional[int] = None
    # The genderLabel property
    gender_label: Optional[str] = None
    # Known values: Unknown (0), Blonde (1), Brown (2), Black (3), Red (4), Auburn (5), Grey (6), White (7), Bald (8), Various (9), Other (10).
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
    # Known values: Unknown (0), Afghan (1), Albanian (2), Algerian (3), Andorran (4), Angolan (5), Antiguan (6), Argentine (7), Armenian (8), Australian (9), Austrian (10), Azerbaijani (11), Bahamian (12), Bahraini (13), Bangladeshi (14), Barbadian (15), Belarusian (16), Belgian (17), Belizean (18), Beninese (19), Bhutanese (20), Bolivian (21), Bosnian (22), Botswanan (23), Brazilian (24), British (25), Bruneian (26), Bulgarian (27), Burkinabe (28), Burundian (29), Cambodian (30), Cameroonian (31), Canadian (32), CapeVerdean (33), CentralAfrican (34), Chadian (35), Chilean (36), Chinese (37), Colombian (38), Comorian (39), Congolese (40), CongoleseDRC (41), CostaRican (42), Croatian (43), Cuban (44), Cypriot (45), Czech (46), Danish (47), Djiboutian (48), Dominican (49), Dutch (50), Ecuadorian (51), Egyptian (52), Emirati (53), EquatorialGuinean (54), Eritrean (55), Estonian (56), Ethiopian (57), Fijian (58), Filipino (59), Finnish (60), French (61), Gabonese (62), Gambian (63), Georgian (64), German (65), Ghanaian (66), Greek (67), Grenadian (68), Guatemalan (69), Guinean (70), GuineaBissauan (71), Guyanese (72), Haitian (73), Honduran (74), Hungarian (75), Icelandic (76), Indian (77), Indonesian (78), Iranian (79), Iraqi (80), Irish (81), Israeli (82), Italian (83), Jamaican (84), Japanese (85), Jordanian (86), Kazakhstani (87), Kenyan (88), Kiribatian (89), Kosovar (90), Kuwaiti (91), Kyrgyz (92), Laotian (93), Latvian (94), Lebanese (95), Liberian (96), Libyan (97), Liechtensteiner (98), Lithuanian (99), Luxembourgish (100), Malagasy (101), Malawian (102), Malaysian (103), Maldivian (104), Malian (105), Maltese (106), Marshallese (107), Mauritanian (108), Mauritian (109), Mexican (110), Micronesian (111), Moldovan (112), Monegasque (113), Mongolian (114), Montenegrin (115), Moroccan (116), Mozambican (117), Burmese (118), Namibian (119), Nauruan (120), Nepali (121), NewZealander (122), Nicaraguan (123), Nigerian (124), Nigerien (125), NorthKorean (126), Norwegian (127), Omani (128), Pakistani (129), Palauan (130), Palestinian (131), Panamanian (132), PapuaNewGuinean (133), Paraguayan (134), Peruvian (135), Polish (136), Portuguese (137), Qatari (138), Romanian (139), Russian (140), Rwandan (141), SaintLucian (142), Salvadoran (143), Sammarinese (144), Samoan (145), SaoTomean (146), Saudi (147), Scottish (148), Senegalese (149), Serbian (150), Seychellois (151), SierraLeonean (152), Singaporean (153), Slovak (154), Slovenian (155), SolomonIslander (156), Somali (157), SouthAfrican (158), SouthKorean (159), SouthSudanese (160), Spanish (161), SriLankan (162), Sudanese (163), Surinamese (164), Swazi (165), Swedish (166), Swiss (167), Syrian (168), Taiwanese (169), Tajik (170), Tanzanian (171), Thai (172), Timorese (173), Togolese (174), Tongan (175), Trinidadian (176), Tunisian (177), Turkish (178), Turkmen (179), Tuvaluan (180), Ugandan (181), Ukrainian (182), Uruguayan (183), Uzbek (184), Vanuatuan (185), Venezuelan (186), Vietnamese (187), Vincentian (188), Welsh (189), Yemeni (190), Zambian (191), Zimbabwean (192).
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
    

