from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class ReportVideoUserImageResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The moderationTargetId property
    moderation_target_id: Optional[UUID] = None
    # The status property
    status: Optional[str] = None
    # The visibility property
    visibility: Optional[str] = None
    # The weightedReportScore property
    weighted_report_score: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ReportVideoUserImageResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ReportVideoUserImageResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ReportVideoUserImageResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "moderationTargetId": lambda n : setattr(self, 'moderation_target_id', n.get_uuid_value()),
            "status": lambda n : setattr(self, 'status', n.get_str_value()),
            "visibility": lambda n : setattr(self, 'visibility', n.get_str_value()),
            "weightedReportScore": lambda n : setattr(self, 'weighted_report_score', n.get_float_value()),
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
        writer.write_uuid_value("moderationTargetId", self.moderation_target_id)
        writer.write_str_value("status", self.status)
        writer.write_str_value("visibility", self.visibility)
        writer.write_float_value("weightedReportScore", self.weighted_report_score)
        writer.write_additional_data_value(self.additional_data)
    

