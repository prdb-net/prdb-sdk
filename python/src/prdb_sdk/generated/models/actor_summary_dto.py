from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class ActorSummaryDto(AdditionalDataHolder, Parsable):
    """
    Summary of a single actor.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Date of birth, if known.
    birthday: Optional[datetime.date] = None
    # Known values: Unknown (0), Caucasian (1), Black (2), Asian (3), Indian (4), Latin (5), MiddleEastern (6), Mixed (7), Other (8).
    ethnicity: Optional[int] = None
    # Human-readable ethnicity label.
    ethnicity_label: Optional[str] = None
    # Known values: Unknown (0), Female (1), Male (2), Intersex (3), Transmale (4), Transfemale (5), NonBinary (6).
    gender: Optional[int] = None
    # Human-readable gender label.
    gender_label: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # Stage name of the actor.
    name: Optional[str] = None
    # Known values: Unknown (0), Afghan (1), Albanian (2), Algerian (3), Andorran (4), Angolan (5), Antiguan (6), Argentine (7), Armenian (8), Australian (9), Austrian (10), Azerbaijani (11), Bahamian (12), Bahraini (13), Bangladeshi (14), Barbadian (15), Belarusian (16), Belgian (17), Belizean (18), Beninese (19), Bhutanese (20), Bolivian (21), Bosnian (22), Botswanan (23), Brazilian (24), British (25), Bruneian (26), Bulgarian (27), Burkinabe (28), Burundian (29), Cambodian (30), Cameroonian (31), Canadian (32), CapeVerdean (33), CentralAfrican (34), Chadian (35), Chilean (36), Chinese (37), Colombian (38), Comorian (39), Congolese (40), CongoleseDRC (41), CostaRican (42), Croatian (43), Cuban (44), Cypriot (45), Czech (46), Danish (47), Djiboutian (48), Dominican (49), Dutch (50), Ecuadorian (51), Egyptian (52), Emirati (53), EquatorialGuinean (54), Eritrean (55), Estonian (56), Ethiopian (57), Fijian (58), Filipino (59), Finnish (60), French (61), Gabonese (62), Gambian (63), Georgian (64), German (65), Ghanaian (66), Greek (67), Grenadian (68), Guatemalan (69), Guinean (70), GuineaBissauan (71), Guyanese (72), Haitian (73), Honduran (74), Hungarian (75), Icelandic (76), Indian (77), Indonesian (78), Iranian (79), Iraqi (80), Irish (81), Israeli (82), Italian (83), Jamaican (84), Japanese (85), Jordanian (86), Kazakhstani (87), Kenyan (88), Kiribatian (89), Kosovar (90), Kuwaiti (91), Kyrgyz (92), Laotian (93), Latvian (94), Lebanese (95), Liberian (96), Libyan (97), Liechtensteiner (98), Lithuanian (99), Luxembourgish (100), Malagasy (101), Malawian (102), Malaysian (103), Maldivian (104), Malian (105), Maltese (106), Marshallese (107), Mauritanian (108), Mauritian (109), Mexican (110), Micronesian (111), Moldovan (112), Monegasque (113), Mongolian (114), Montenegrin (115), Moroccan (116), Mozambican (117), Burmese (118), Namibian (119), Nauruan (120), Nepali (121), NewZealander (122), Nicaraguan (123), Nigerian (124), Nigerien (125), NorthKorean (126), Norwegian (127), Omani (128), Pakistani (129), Palauan (130), Palestinian (131), Panamanian (132), PapuaNewGuinean (133), Paraguayan (134), Peruvian (135), Polish (136), Portuguese (137), Qatari (138), Romanian (139), Russian (140), Rwandan (141), SaintLucian (142), Salvadoran (143), Sammarinese (144), Samoan (145), SaoTomean (146), Saudi (147), Scottish (148), Senegalese (149), Serbian (150), Seychellois (151), SierraLeonean (152), Singaporean (153), Slovak (154), Slovenian (155), SolomonIslander (156), Somali (157), SouthAfrican (158), SouthKorean (159), SouthSudanese (160), Spanish (161), SriLankan (162), Sudanese (163), Surinamese (164), Swazi (165), Swedish (166), Swiss (167), Syrian (168), Taiwanese (169), Tajik (170), Tanzanian (171), Thai (172), Timorese (173), Togolese (174), Tongan (175), Trinidadian (176), Tunisian (177), Turkish (178), Turkmen (179), Tuvaluan (180), Ugandan (181), Ukrainian (182), Uruguayan (183), Uzbek (184), Vanuatuan (185), Venezuelan (186), Vietnamese (187), Vincentian (188), Welsh (189), Yemeni (190), Zambian (191), Zimbabwean (192).
    nationality: Optional[int] = None
    # Human-readable nationality label.
    nationality_label: Optional[str] = None
    # Full CDN URL of the actor's profile image, if available.
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
    

