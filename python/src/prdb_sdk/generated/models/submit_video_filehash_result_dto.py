from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class SubmitVideoFilehashResultDto(AdditionalDataHolder, Parsable):
    """
    What happened to one submitted assignment.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The OS hash of the entry, normalized to upper case.
    os_hash: Optional[str] = None
    # Outcome of a single submission. Known values: Recorded (0), Updated (1), Conflicted (2), VideoNotFound (3).
    outcome: Optional[int] = None
    # The video the entry named.
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SubmitVideoFilehashResultDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SubmitVideoFilehashResultDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SubmitVideoFilehashResultDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "osHash": lambda n : setattr(self, 'os_hash', n.get_str_value()),
            "outcome": lambda n : setattr(self, 'outcome', n.get_int_value()),
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
        writer.write_str_value("osHash", self.os_hash)
        writer.write_int_value("outcome", self.outcome)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

