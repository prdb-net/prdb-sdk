from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .indexer_filehash_lookup_key_dto import IndexerFilehashLookupKeyDto

@dataclass
class LookupIndexerFilehashesRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The filenames property
    filenames: Optional[list[str]] = None
    # The filesizes property
    filesizes: Optional[list[int]] = None
    # The ids property
    ids: Optional[list[UUID]] = None
    # The indexerKeys property
    indexer_keys: Optional[list[IndexerFilehashLookupKeyDto]] = None
    # The osHashes property
    os_hashes: Optional[list[str]] = None
    # The pHashes property
    p_hashes: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> LookupIndexerFilehashesRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: LookupIndexerFilehashesRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return LookupIndexerFilehashesRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .indexer_filehash_lookup_key_dto import IndexerFilehashLookupKeyDto

        from .indexer_filehash_lookup_key_dto import IndexerFilehashLookupKeyDto

        fields: dict[str, Callable[[Any], None]] = {
            "filenames": lambda n : setattr(self, 'filenames', n.get_collection_of_primitive_values(str)),
            "filesizes": lambda n : setattr(self, 'filesizes', n.get_collection_of_primitive_values(int)),
            "ids": lambda n : setattr(self, 'ids', n.get_collection_of_primitive_values(UUID)),
            "indexerKeys": lambda n : setattr(self, 'indexer_keys', n.get_collection_of_object_values(IndexerFilehashLookupKeyDto)),
            "osHashes": lambda n : setattr(self, 'os_hashes', n.get_collection_of_primitive_values(str)),
            "pHashes": lambda n : setattr(self, 'p_hashes', n.get_collection_of_primitive_values(str)),
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
        writer.write_collection_of_primitive_values("filenames", self.filenames)
        writer.write_collection_of_primitive_values("filesizes", self.filesizes)
        writer.write_collection_of_primitive_values("ids", self.ids)
        writer.write_collection_of_object_values("indexerKeys", self.indexer_keys)
        writer.write_collection_of_primitive_values("osHashes", self.os_hashes)
        writer.write_collection_of_primitive_values("pHashes", self.p_hashes)
        writer.write_additional_data_value(self.additional_data)
    

