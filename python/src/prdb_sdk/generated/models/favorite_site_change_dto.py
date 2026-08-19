from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .favorite_site_change_favorite_site_dto import FavoriteSiteChangeFavoriteSiteDto

@dataclass
class FavoriteSiteChangeDto(AdditionalDataHolder, Parsable):
    """
    A single changed favorite site row in the incremental feed.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # One of `created`, `updated`, or `deleted`.
    event_type: Optional[str] = None
    # Current-state payload for a favorite site row in the incremental feed.
    favorite_site: Optional[FavoriteSiteChangeFavoriteSiteDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FavoriteSiteChangeDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FavoriteSiteChangeDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FavoriteSiteChangeDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .favorite_site_change_favorite_site_dto import FavoriteSiteChangeFavoriteSiteDto

        from .favorite_site_change_favorite_site_dto import FavoriteSiteChangeFavoriteSiteDto

        fields: dict[str, Callable[[Any], None]] = {
            "eventType": lambda n : setattr(self, 'event_type', n.get_str_value()),
            "favoriteSite": lambda n : setattr(self, 'favorite_site', n.get_object_value(FavoriteSiteChangeFavoriteSiteDto)),
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
        writer.write_str_value("eventType", self.event_type)
        writer.write_object_value("favoriteSite", self.favorite_site)
        writer.write_additional_data_value(self.additional_data)
    

