from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .fulfillment_app import FulfillmentApp
    from .update_wanted_video_request_fulfillment_by_app_member1 import UpdateWantedVideoRequest_fulfillmentByAppMember1

@dataclass
class UpdateWantedVideoRequest_fulfillmentByApp(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes FulfillmentApp, UpdateWantedVideoRequest_fulfillmentByAppMember1
    """
    # Composed type representation for type FulfillmentApp
    fulfillment_app: Optional[FulfillmentApp] = None
    # Composed type representation for type UpdateWantedVideoRequest_fulfillmentByAppMember1
    update_wanted_video_request_fulfillment_by_app_member1: Optional[UpdateWantedVideoRequest_fulfillmentByAppMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdateWantedVideoRequest_fulfillmentByApp:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdateWantedVideoRequest_fulfillmentByApp
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = UpdateWantedVideoRequest_fulfillmentByApp()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .fulfillment_app import FulfillmentApp
        from .update_wanted_video_request_fulfillment_by_app_member1 import UpdateWantedVideoRequest_fulfillmentByAppMember1

        if self.fulfillment_app:
            return self.fulfillment_app.get_field_deserializers()
        if self.update_wanted_video_request_fulfillment_by_app_member1:
            return self.update_wanted_video_request_fulfillment_by_app_member1.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.fulfillment_app:
            writer.write_object_value(None, self.fulfillment_app)
        elif self.update_wanted_video_request_fulfillment_by_app_member1:
            writer.write_object_value(None, self.update_wanted_video_request_fulfillment_by_app_member1)
    

