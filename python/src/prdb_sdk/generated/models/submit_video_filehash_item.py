from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class SubmitVideoFilehashItem(AdditionalDataHolder, Parsable):
    """
    A single hash-to-video assignment.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # File name without directory. Optional — a client may withhold it, and the endpoint works without it.
    filename: Optional[str] = None
    # Size of the file in bytes.
    filesize: Optional[int] = None
    # OS hash of the file, 16 hexadecimal characters. Required; it is the only aggregation key.
    os_hash: Optional[str] = None
    # Perceptual hash of the file, 16 hexadecimal characters, if the client computed one. It mustbe computed as "Perceptual hashes" in the API description prescribes; a submission carryinga value from another procedure contributes a row nothing can match.
    p_hash: Optional[str] = None
    # The scene release name the file came in, if the client knows one. Optional. It is a releasename, not a file name: send it when the acquisition carried one, and leave it out otherwise.
    release_name: Optional[str] = None
    # Known values: UserConfirmed (0), ClientDetected (1).
    source: Optional[int] = None
    # The video this file is. Required — a hash observation without an assignment is not accepted.
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SubmitVideoFilehashItem:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SubmitVideoFilehashItem
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SubmitVideoFilehashItem()
    
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
            "releaseName": lambda n : setattr(self, 'release_name', n.get_str_value()),
            "source": lambda n : setattr(self, 'source', n.get_int_value()),
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
        writer.write_str_value("filename", self.filename)
        writer.write_int_value("filesize", self.filesize)
        writer.write_str_value("osHash", self.os_hash)
        writer.write_str_value("pHash", self.p_hash)
        writer.write_str_value("releaseName", self.release_name)
        writer.write_int_value("source", self.source)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

