from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class IdentifyVideoFileDto(AdditionalDataHolder, Parsable):
    """
    One file to identify.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # File name without directory. Required — it carries the lowest rungs of the ladder.
    filename: Optional[str] = None
    # Size of the file in bytes, if known.
    filesize: Optional[int] = None
    # OS hash of the file, 16 hexadecimal characters, if the client computed one.
    os_hash: Optional[str] = None
    # Perceptual hash of the file, 16 hexadecimal characters, if the client computed one.Compared for equality only, and only against values computed the way "Perceptual hashes"in the API description prescribes — send none rather than one from another procedure.
    p_hash: Optional[str] = None
    # Client-assigned identifier, returned unchanged. Unique within the request.
    ref: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IdentifyVideoFileDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IdentifyVideoFileDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IdentifyVideoFileDto()
    
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
            "ref": lambda n : setattr(self, 'ref', n.get_str_value()),
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
        writer.write_str_value("ref", self.ref)
        writer.write_additional_data_value(self.additional_data)
    

