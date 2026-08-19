from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .wanted_video_summary_dto import WantedVideoSummaryDto

@dataclass
class ListWantedVideosResponse(AdditionalDataHolder, Parsable):
    """
    Paged list of the current user's wanted videos.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Wanted video entries on the current page.
    items: Optional[list[WantedVideoSummaryDto]] = None
    # Current page number (1-based).
    page: Optional[int] = None
    # Number of items per page.
    page_size: Optional[int] = None
    # Field the results are sorted by.
    sort_by: Optional[str] = None
    # Sort direction applied: `asc` or `desc`.
    sort_direction: Optional[str] = None
    # Total number of wanted videos matching the current query filters.
    total_count: Optional[int] = None
    # Total number of pages.
    total_pages: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ListWantedVideosResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ListWantedVideosResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ListWantedVideosResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .wanted_video_summary_dto import WantedVideoSummaryDto

        from .wanted_video_summary_dto import WantedVideoSummaryDto

        fields: dict[str, Callable[[Any], None]] = {
            "items": lambda n : setattr(self, 'items', n.get_collection_of_object_values(WantedVideoSummaryDto)),
            "page": lambda n : setattr(self, 'page', n.get_int_value()),
            "pageSize": lambda n : setattr(self, 'page_size', n.get_int_value()),
            "sortBy": lambda n : setattr(self, 'sort_by', n.get_str_value()),
            "sortDirection": lambda n : setattr(self, 'sort_direction', n.get_str_value()),
            "totalCount": lambda n : setattr(self, 'total_count', n.get_int_value()),
            "totalPages": lambda n : setattr(self, 'total_pages', n.get_int_value()),
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
        writer.write_int_value("totalPages", self.total_pages)
        writer.write_additional_data_value(self.additional_data)
    

