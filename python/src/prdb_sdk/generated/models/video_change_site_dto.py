from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .video_change_network_dto import VideoChangeNetworkDto

@dataclass
class VideoChangeSiteDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Public account handle, independent of the local Site UUID.
    account_handle: Optional[str] = None
    # The id property
    id: Optional[UUID] = None
    # The network property
    network: Optional[VideoChangeNetworkDto] = None
    # Publishing platform UUID; null for classic studio sites.
    platform_id: Optional[UUID] = None
    # Stable publishing platform key; null for classic sites.
    platform_key: Optional[str] = None
    # Publishing platform display title; null for classic sites.
    platform_title: Optional[str] = None
    # The title property
    title: Optional[str] = None
    # The url property
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoChangeSiteDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoChangeSiteDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoChangeSiteDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .video_change_network_dto import VideoChangeNetworkDto

        from .video_change_network_dto import VideoChangeNetworkDto

        fields: dict[str, Callable[[Any], None]] = {
            "accountHandle": lambda n : setattr(self, 'account_handle', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "network": lambda n : setattr(self, 'network', n.get_object_value(VideoChangeNetworkDto)),
            "platformId": lambda n : setattr(self, 'platform_id', n.get_uuid_value()),
            "platformKey": lambda n : setattr(self, 'platform_key', n.get_str_value()),
            "platformTitle": lambda n : setattr(self, 'platform_title', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "url": lambda n : setattr(self, 'url', n.get_str_value()),
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
        writer.write_str_value("accountHandle", self.account_handle)
        writer.write_uuid_value("id", self.id)
        writer.write_object_value("network", self.network)
        writer.write_uuid_value("platformId", self.platform_id)
        writer.write_str_value("platformKey", self.platform_key)
        writer.write_str_value("platformTitle", self.platform_title)
        writer.write_str_value("title", self.title)
        writer.write_str_value("url", self.url)
        writer.write_additional_data_value(self.additional_data)
    

