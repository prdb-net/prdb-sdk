from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .identify_freshness_result_dto_status import IdentifyFreshnessResultDto_status
    from .identify_video_result_dto import IdentifyVideoResultDto

@dataclass
class IdentifyFreshnessResultDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ref property
    ref: Optional[str] = None
    # What the identification ladder made of one file.
    result: Optional[IdentifyVideoResultDto] = None
    # unchanged: reuse retained Identification, not Video details; identified: replace with result; reidentify: no proof. Allowed values: unchanged, identified, reidentify.
    status: Optional[IdentifyFreshnessResultDto_status] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IdentifyFreshnessResultDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IdentifyFreshnessResultDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IdentifyFreshnessResultDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .identify_freshness_result_dto_status import IdentifyFreshnessResultDto_status
        from .identify_video_result_dto import IdentifyVideoResultDto

        from .identify_freshness_result_dto_status import IdentifyFreshnessResultDto_status
        from .identify_video_result_dto import IdentifyVideoResultDto

        fields: dict[str, Callable[[Any], None]] = {
            "ref": lambda n : setattr(self, 'ref', n.get_str_value()),
            "result": lambda n : setattr(self, 'result', n.get_object_value(IdentifyVideoResultDto)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(IdentifyFreshnessResultDto_status)),
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
        writer.write_str_value("ref", self.ref)
        writer.write_object_value("result", self.result)
        writer.write_enum_value("status", self.status)
        writer.write_additional_data_value(self.additional_data)
    

