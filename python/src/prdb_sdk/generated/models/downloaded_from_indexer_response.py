from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .downloaded_from_indexer_filename_dto import DownloadedFromIndexerFilenameDto

@dataclass
class DownloadedFromIndexerResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The downloadIdentifier property
    download_identifier: Optional[str] = None
    # The filenames property
    filenames: Optional[list[DownloadedFromIndexerFilenameDto]] = None
    # The id property
    id: Optional[UUID] = None
    # The indexerId property
    indexer_id: Optional[str] = None
    # Known values: DrunkenSlug (0), NzbFinder (1), NzbPorn (2).
    indexer_source: Optional[int] = None
    # The nzbName property
    nzb_name: Optional[str] = None
    # The nzbUrl property
    nzb_url: Optional[str] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    # The videoId property
    video_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DownloadedFromIndexerResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DownloadedFromIndexerResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DownloadedFromIndexerResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .downloaded_from_indexer_filename_dto import DownloadedFromIndexerFilenameDto

        from .downloaded_from_indexer_filename_dto import DownloadedFromIndexerFilenameDto

        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "downloadIdentifier": lambda n : setattr(self, 'download_identifier', n.get_str_value()),
            "filenames": lambda n : setattr(self, 'filenames', n.get_collection_of_object_values(DownloadedFromIndexerFilenameDto)),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "indexerId": lambda n : setattr(self, 'indexer_id', n.get_str_value()),
            "indexerSource": lambda n : setattr(self, 'indexer_source', n.get_int_value()),
            "nzbName": lambda n : setattr(self, 'nzb_name', n.get_str_value()),
            "nzbUrl": lambda n : setattr(self, 'nzb_url', n.get_str_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
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
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_str_value("downloadIdentifier", self.download_identifier)
        writer.write_collection_of_object_values("filenames", self.filenames)
        writer.write_uuid_value("id", self.id)
        writer.write_str_value("indexerId", self.indexer_id)
        writer.write_int_value("indexerSource", self.indexer_source)
        writer.write_str_value("nzbName", self.nzb_name)
        writer.write_str_value("nzbUrl", self.nzb_url)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_additional_data_value(self.additional_data)
    

