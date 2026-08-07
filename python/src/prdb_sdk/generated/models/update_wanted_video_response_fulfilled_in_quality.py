from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .update_wanted_video_response_fulfilled_in_quality_member1 import UpdateWantedVideoResponse_fulfilledInQualityMember1
    from .video_quality import VideoQuality

@dataclass
class UpdateWantedVideoResponse_fulfilledInQuality(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes UpdateWantedVideoResponse_fulfilledInQualityMember1, VideoQuality
    """
    # Composed type representation for type UpdateWantedVideoResponse_fulfilledInQualityMember1
    update_wanted_video_response_fulfilled_in_quality_member1: Optional[UpdateWantedVideoResponse_fulfilledInQualityMember1] = None
    # Composed type representation for type VideoQuality
    video_quality: Optional[VideoQuality] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdateWantedVideoResponse_fulfilledInQuality:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdateWantedVideoResponse_fulfilledInQuality
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = UpdateWantedVideoResponse_fulfilledInQuality()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .update_wanted_video_response_fulfilled_in_quality_member1 import UpdateWantedVideoResponse_fulfilledInQualityMember1
        from .video_quality import VideoQuality

        if self.update_wanted_video_response_fulfilled_in_quality_member1:
            return self.update_wanted_video_response_fulfilled_in_quality_member1.get_field_deserializers()
        if self.video_quality:
            return self.video_quality.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.update_wanted_video_response_fulfilled_in_quality_member1:
            writer.write_object_value(None, self.update_wanted_video_response_fulfilled_in_quality_member1)
        elif self.video_quality:
            writer.write_object_value(None, self.video_quality)
    

