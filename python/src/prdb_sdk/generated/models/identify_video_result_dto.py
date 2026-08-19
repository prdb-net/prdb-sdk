from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .identify_site_dto import IdentifySiteDto
    from .video_detail_dto import VideoDetailDto

@dataclass
class IdentifyVideoResultDto(AdditionalDataHolder, Parsable):
    """
    What the identification ladder made of one file.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # All equally good videos when the match was ambiguous; otherwise empty.
    candidates: Optional[list[UUID]] = None
    # How much the match can be trusted. Drives whether a client files a file automatically. Known values: None (0), Partial (1), Probable (2), Strong (3), Exact (4), Ambiguous (5).
    confidence: Optional[int] = None
    # Known values: OsHash (0), PHash (1), Filename (2), ReleaseName (3), Site (4).
    matched_by: Optional[int] = None
    # The client-assigned identifier of the input file, returned unchanged.
    ref: Optional[str] = None
    # The site a file could be attributed to.
    site: Optional[IdentifySiteDto] = None
    # The video property
    video: Optional[VideoDetailDto] = None
    # The identified video, when exactly one was found.
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IdentifyVideoResultDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IdentifyVideoResultDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IdentifyVideoResultDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .identify_site_dto import IdentifySiteDto
        from .video_detail_dto import VideoDetailDto

        from .identify_site_dto import IdentifySiteDto
        from .video_detail_dto import VideoDetailDto

        fields: dict[str, Callable[[Any], None]] = {
            "candidates": lambda n : setattr(self, 'candidates', n.get_collection_of_primitive_values(UUID)),
            "confidence": lambda n : setattr(self, 'confidence', n.get_int_value()),
            "matchedBy": lambda n : setattr(self, 'matched_by', n.get_int_value()),
            "ref": lambda n : setattr(self, 'ref', n.get_str_value()),
            "site": lambda n : setattr(self, 'site', n.get_object_value(IdentifySiteDto)),
            "video": lambda n : setattr(self, 'video', n.get_object_value(VideoDetailDto)),
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
        writer.write_collection_of_primitive_values("candidates", self.candidates)
        writer.write_int_value("confidence", self.confidence)
        writer.write_int_value("matchedBy", self.matched_by)
        writer.write_str_value("ref", self.ref)
        writer.write_object_value("site", self.site)
        writer.write_object_value("video", self.video)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

