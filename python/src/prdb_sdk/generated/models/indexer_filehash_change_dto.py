from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .indexer_filehash_change_filehash_dto import IndexerFilehashChangeFilehashDto

@dataclass
class IndexerFilehashChangeDto(AdditionalDataHolder, Parsable):
    """
    A single changed indexer filehash row in the incremental feed.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # One of `created`, `updated`, or `deleted`.
    event_type: Optional[str] = None
    # Current persisted state of a changed indexer filehash row, including soft-delete fields.
    filehash: Optional[IndexerFilehashChangeFilehashDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IndexerFilehashChangeDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IndexerFilehashChangeDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IndexerFilehashChangeDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .indexer_filehash_change_filehash_dto import IndexerFilehashChangeFilehashDto

        from .indexer_filehash_change_filehash_dto import IndexerFilehashChangeFilehashDto

        fields: dict[str, Callable[[Any], None]] = {
            "eventType": lambda n : setattr(self, 'event_type', n.get_str_value()),
            "filehash": lambda n : setattr(self, 'filehash', n.get_object_value(IndexerFilehashChangeFilehashDto)),
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
        writer.write_str_value("eventType", self.event_type)
        writer.write_object_value("filehash", self.filehash)
        writer.write_additional_data_value(self.additional_data)
    

