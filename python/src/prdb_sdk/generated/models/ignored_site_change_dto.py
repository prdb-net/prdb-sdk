from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .ignored_site_change_ignored_site_dto import IgnoredSiteChangeIgnoredSiteDto

@dataclass
class IgnoredSiteChangeDto(AdditionalDataHolder, Parsable):
    """
    A single changed ignored site row in the incremental feed.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # One of `created`, `updated`, or `deleted`.
    event_type: Optional[str] = None
    # Current-state payload for an ignored site row in the incremental feed.
    ignored_site: Optional[IgnoredSiteChangeIgnoredSiteDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IgnoredSiteChangeDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IgnoredSiteChangeDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IgnoredSiteChangeDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .ignored_site_change_ignored_site_dto import IgnoredSiteChangeIgnoredSiteDto

        from .ignored_site_change_ignored_site_dto import IgnoredSiteChangeIgnoredSiteDto

        fields: dict[str, Callable[[Any], None]] = {
            "eventType": lambda n : setattr(self, 'event_type', n.get_str_value()),
            "ignoredSite": lambda n : setattr(self, 'ignored_site', n.get_object_value(IgnoredSiteChangeIgnoredSiteDto)),
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
        writer.write_object_value("ignoredSite", self.ignored_site)
        writer.write_additional_data_value(self.additional_data)
    

