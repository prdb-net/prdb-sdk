from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class BaselineDocumentTooLargeResponse(APIError, AdditionalDataHolder, Parsable):
    """
    Fetch this single document through GET /videos/{videoId}, persist it, then resume.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The changesSince property
    changes_since: Optional[datetime.datetime] = None
    # The nextCursor property
    next_cursor: Optional[str] = None
    # The videoId property
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BaselineDocumentTooLargeResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BaselineDocumentTooLargeResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BaselineDocumentTooLargeResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "changesSince": lambda n : setattr(self, 'changes_since', n.get_datetime_value()),
            "nextCursor": lambda n : setattr(self, 'next_cursor', n.get_str_value()),
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
        writer.write_datetime_value("changesSince", self.changes_since)
        writer.write_str_value("nextCursor", self.next_cursor)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def primary_message(self) -> Optional[str]:
        """
        The primary error message.
        """
        return super().message

