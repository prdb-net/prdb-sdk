from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .video_quality import VideoQuality
    from .wanted_video_summary_dto_fulfilled_in_quality_member1 import WantedVideoSummaryDto_fulfilledInQualityMember1

@dataclass
class WantedVideoSummaryDto_fulfilledInQuality(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes VideoQuality, WantedVideoSummaryDto_fulfilledInQualityMember1
    """
    # Composed type representation for type VideoQuality
    video_quality: Optional[VideoQuality] = None
    # Composed type representation for type WantedVideoSummaryDto_fulfilledInQualityMember1
    wanted_video_summary_dto_fulfilled_in_quality_member1: Optional[WantedVideoSummaryDto_fulfilledInQualityMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WantedVideoSummaryDto_fulfilledInQuality:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WantedVideoSummaryDto_fulfilledInQuality
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = WantedVideoSummaryDto_fulfilledInQuality()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_quality import VideoQuality
        from .wanted_video_summary_dto_fulfilled_in_quality_member1 import WantedVideoSummaryDto_fulfilledInQualityMember1

        if self.video_quality:
            return self.video_quality.get_field_deserializers()
        if self.wanted_video_summary_dto_fulfilled_in_quality_member1:
            return self.wanted_video_summary_dto_fulfilled_in_quality_member1.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.video_quality:
            writer.write_object_value(None, self.video_quality)
        elif self.wanted_video_summary_dto_fulfilled_in_quality_member1:
            writer.write_object_value(None, self.wanted_video_summary_dto_fulfilled_in_quality_member1)
    

