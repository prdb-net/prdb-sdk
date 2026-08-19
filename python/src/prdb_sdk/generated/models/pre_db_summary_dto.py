from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class PreDbSummaryDto(AdditionalDataHolder, Parsable):
    """
    Summary representation of a PreDb entry.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Readable category value: Movies, TvShows, or Adult.
    category: Optional[str] = None
    # Optional file size value if known.
    filesize: Optional[int] = None
    # Unique identifier of the PreDb entry.
    id: Optional[UUID] = None
    # Release date associated with the entry.
    release_date: Optional[datetime.date] = None
    # Release group name.
    release_group: Optional[str] = None
    # Release title as indexed in PreDb.
    title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PreDbSummaryDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PreDbSummaryDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PreDbSummaryDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "category": lambda n : setattr(self, 'category', n.get_str_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "releaseDate": lambda n : setattr(self, 'release_date', n.get_date_value()),
            "releaseGroup": lambda n : setattr(self, 'release_group', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
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
        writer.write_str_value("category", self.category)
        writer.write_int_value("filesize", self.filesize)
        writer.write_uuid_value("id", self.id)
        writer.write_date_value("releaseDate", self.release_date)
        writer.write_str_value("releaseGroup", self.release_group)
        writer.write_str_value("title", self.title)
        writer.write_additional_data_value(self.additional_data)
    

