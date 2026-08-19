from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class UpdateDownloadedFromIndexerRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Download identifier returned by the indexer or download client.
    download_identifier: Optional[str] = None
    # Indexer-specific identifier for the download item.
    indexer_id: Optional[str] = None
    # Known values: DrunkenSlug (0), NzbFinder (1), NzbPorn (2).
    indexer_source: Optional[int] = None
    # NZB or release name.
    nzb_name: Optional[str] = None
    # NZB or release URL.
    nzb_url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdateDownloadedFromIndexerRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdateDownloadedFromIndexerRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UpdateDownloadedFromIndexerRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "downloadIdentifier": lambda n : setattr(self, 'download_identifier', n.get_str_value()),
            "indexerId": lambda n : setattr(self, 'indexer_id', n.get_str_value()),
            "indexerSource": lambda n : setattr(self, 'indexer_source', n.get_int_value()),
            "nzbName": lambda n : setattr(self, 'nzb_name', n.get_str_value()),
            "nzbUrl": lambda n : setattr(self, 'nzb_url', n.get_str_value()),
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
        writer.write_str_value("downloadIdentifier", self.download_identifier)
        writer.write_str_value("indexerId", self.indexer_id)
        writer.write_int_value("indexerSource", self.indexer_source)
        writer.write_str_value("nzbName", self.nzb_name)
        writer.write_str_value("nzbUrl", self.nzb_url)
        writer.write_additional_data_value(self.additional_data)
    

