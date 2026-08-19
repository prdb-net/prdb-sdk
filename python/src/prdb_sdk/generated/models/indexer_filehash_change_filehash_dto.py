from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class IndexerFilehashChangeFilehashDto(AdditionalDataHolder, Parsable):
    """
    Current persisted state of a changed indexer filehash row, including soft-delete fields.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # Timestamp when the row was soft-deleted, or null when still active.
    deleted_at_utc: Optional[datetime.datetime] = None
    # Original filename submitted for this filehash record.
    filename: Optional[str] = None
    # File size in bytes.
    filesize: Optional[int] = None
    # The id property
    id: Optional[UUID] = None
    # Indexer-specific identifier for the release.
    indexer_id: Optional[str] = None
    # Indexer source. Supported values: `DrunkenSlug`, `NzbFinder`, `NzbPorn`.
    indexer_source: Optional[str] = None
    # Whether this row is soft-deleted.
    is_deleted: Optional[bool] = None
    # Whether this filehash record has been verified.
    is_verified: Optional[bool] = None
    # OS hash value as stored.
    os_hash: Optional[str] = None
    # P hash value as stored, or null when not available.
    p_hash: Optional[str] = None
    # Number of submissions merged into this filehash record.
    submission_count: Optional[int] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IndexerFilehashChangeFilehashDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IndexerFilehashChangeFilehashDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IndexerFilehashChangeFilehashDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "deletedAtUtc": lambda n : setattr(self, 'deleted_at_utc', n.get_datetime_value()),
            "filename": lambda n : setattr(self, 'filename', n.get_str_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "indexerId": lambda n : setattr(self, 'indexer_id', n.get_str_value()),
            "indexerSource": lambda n : setattr(self, 'indexer_source', n.get_str_value()),
            "isDeleted": lambda n : setattr(self, 'is_deleted', n.get_bool_value()),
            "isVerified": lambda n : setattr(self, 'is_verified', n.get_bool_value()),
            "osHash": lambda n : setattr(self, 'os_hash', n.get_str_value()),
            "pHash": lambda n : setattr(self, 'p_hash', n.get_str_value()),
            "submissionCount": lambda n : setattr(self, 'submission_count', n.get_int_value()),
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
        writer.write_datetime_value("deletedAtUtc", self.deleted_at_utc)
        writer.write_str_value("filename", self.filename)
        writer.write_int_value("filesize", self.filesize)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("indexerId", self.indexer_id)
        writer.write_str_value("indexerSource", self.indexer_source)
        writer.write_bool_value("isDeleted", self.is_deleted)
        writer.write_bool_value("isVerified", self.is_verified)
        writer.write_str_value("osHash", self.os_hash)
        writer.write_str_value("pHash", self.p_hash)
        writer.write_int_value("submissionCount", self.submission_count)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_additional_data_value(self.additional_data)
    

