from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .video_filehash_dto import VideoFilehashDto

@dataclass
class UnlinkedVideoFilehashesResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The items property
    items: Optional[list[VideoFilehashDto]] = None
    # The page property
    page: Optional[int] = None
    # The pageSize property
    page_size: Optional[int] = None
    # The sortBy property
    sort_by: Optional[str] = None
    # The sortDirection property
    sort_direction: Optional[str] = None
    # The totalCount property
    total_count: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UnlinkedVideoFilehashesResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UnlinkedVideoFilehashesResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UnlinkedVideoFilehashesResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_filehash_dto import VideoFilehashDto

        from .video_filehash_dto import VideoFilehashDto

        fields: dict[str, Callable[[Any], None]] = {
            "items": lambda n : setattr(self, 'items', n.get_collection_of_object_values(VideoFilehashDto)),
            "page": lambda n : setattr(self, 'page', n.get_int_value()),
            "pageSize": lambda n : setattr(self, 'page_size', n.get_int_value()),
            "sortBy": lambda n : setattr(self, 'sort_by', n.get_str_value()),
            "sortDirection": lambda n : setattr(self, 'sort_direction', n.get_str_value()),
            "totalCount": lambda n : setattr(self, 'total_count', n.get_int_value()),
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
        writer.write_collection_of_object_values("items", self.items)
        writer.write_int_value("page", self.page)
        writer.write_int_value("pageSize", self.page_size)
        writer.write_str_value("sortBy", self.sort_by)
        writer.write_str_value("sortDirection", self.sort_direction)
        writer.write_int_value("totalCount", self.total_count)
        writer.write_additional_data_value(self.additional_data)
    

