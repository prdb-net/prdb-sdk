from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class DownloadedFromIndexerFilenameDto(AdditionalDataHolder, Parsable):
    """
    A filename recorded for a downloaded-from-indexer entry.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # When this filename row was created.
    created_at_utc: Optional[datetime.datetime] = None
    # ID of the parent downloaded-from-indexer entry.
    downloaded_from_indexer_id: Optional[UUID] = None
    # The filename as reported by the indexer/download source.
    filename: Optional[str] = None
    # File size in bytes.
    filesize: Optional[int] = None
    # ID of the filename row.
    id: Optional[UUID] = None
    # Optional OS hash value as a 16-character fixed-length string.
    os_hash: Optional[str] = None
    # Optional perceptual hash value as a 16-character fixed-length string.
    p_hash: Optional[str] = None
    # When this filename row was last updated.
    updated_at_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DownloadedFromIndexerFilenameDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DownloadedFromIndexerFilenameDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DownloadedFromIndexerFilenameDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "downloadedFromIndexerId": lambda n : setattr(self, 'downloaded_from_indexer_id', n.get_uuid_value()),
            "filename": lambda n : setattr(self, 'filename', n.get_str_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "osHash": lambda n : setattr(self, 'os_hash', n.get_str_value()),
            "pHash": lambda n : setattr(self, 'p_hash', n.get_str_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
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
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_uuid_value("downloadedFromIndexerId", self.downloaded_from_indexer_id)
        writer.write_str_value("filename", self.filename)
        writer.write_int_value("filesize", self.filesize)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("osHash", self.os_hash)
        writer.write_str_value("pHash", self.p_hash)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_additional_data_value(self.additional_data)
    

