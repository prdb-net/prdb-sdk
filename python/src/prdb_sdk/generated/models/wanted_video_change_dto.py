from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .wanted_video_change_wanted_video_dto import WantedVideoChangeWantedVideoDto

@dataclass
class WantedVideoChangeDto(AdditionalDataHolder, Parsable):
    """
    A single changed wanted video row in the incremental feed.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # One of `created`, `updated`, or `deleted`.
    event_type: Optional[str] = None
    # Current-state payload for a wanted video row in the incremental feed.
    wanted_video: Optional[WantedVideoChangeWantedVideoDto] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WantedVideoChangeDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WantedVideoChangeDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WantedVideoChangeDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .wanted_video_change_wanted_video_dto import WantedVideoChangeWantedVideoDto

        from .wanted_video_change_wanted_video_dto import WantedVideoChangeWantedVideoDto

        fields: dict[str, Callable[[Any], None]] = {
            "eventType": lambda n : setattr(self, 'event_type', n.get_str_value()),
            "wantedVideo": lambda n : setattr(self, 'wanted_video', n.get_object_value(WantedVideoChangeWantedVideoDto)),
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
        writer.write_object_value("wantedVideo", self.wanted_video)
        writer.write_additional_data_value(self.additional_data)
    

