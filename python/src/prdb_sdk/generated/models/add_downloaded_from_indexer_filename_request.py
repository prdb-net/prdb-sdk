from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class AddDownloadedFromIndexerFilenameRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The filename as reported by the indexer/download source.
    filename: Optional[str] = None
    # File size in bytes.
    filesize: Optional[int] = None
    # Optional OS hash value as a 16-character fixed-length string.
    os_hash: Optional[str] = None
    # Optional perceptual hash value, 16 hexadecimal characters. It must be computed as"Perceptual hashes" in the API description prescribes; a value from another procedureis stored but can never be matched.
    p_hash: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AddDownloadedFromIndexerFilenameRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AddDownloadedFromIndexerFilenameRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AddDownloadedFromIndexerFilenameRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "filename": lambda n : setattr(self, 'filename', n.get_str_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "osHash": lambda n : setattr(self, 'os_hash', n.get_str_value()),
            "pHash": lambda n : setattr(self, 'p_hash', n.get_str_value()),
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
        writer.write_str_value("filename", self.filename)
        writer.write_int_value("filesize", self.filesize)
        writer.write_str_value("osHash", self.os_hash)
        writer.write_str_value("pHash", self.p_hash)
        writer.write_additional_data_value(self.additional_data)
    

