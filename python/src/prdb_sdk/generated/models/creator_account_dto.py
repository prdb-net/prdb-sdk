from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class CreatorAccountDto(AdditionalDataHolder, Parsable):
    """
    Confirmed catalogue ownership. Credits and private source identities are excluded.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The accountHandle property
    account_handle: Optional[str] = None
    # The actorId property
    actor_id: Optional[UUID] = None
    # The actorName property
    actor_name: Optional[str] = None
    # The platformId property
    platform_id: Optional[UUID] = None
    # The platformKey property
    platform_key: Optional[str] = None
    # The platformTitle property
    platform_title: Optional[str] = None
    # The siteId property
    site_id: Optional[UUID] = None
    # The siteTitle property
    site_title: Optional[str] = None
    # The url property
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreatorAccountDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreatorAccountDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreatorAccountDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "accountHandle": lambda n : setattr(self, 'account_handle', n.get_str_value()),
            "actorId": lambda n : setattr(self, 'actor_id', n.get_uuid_value()),
            "actorName": lambda n : setattr(self, 'actor_name', n.get_str_value()),
            "platformId": lambda n : setattr(self, 'platform_id', n.get_uuid_value()),
            "platformKey": lambda n : setattr(self, 'platform_key', n.get_str_value()),
            "platformTitle": lambda n : setattr(self, 'platform_title', n.get_str_value()),
            "siteId": lambda n : setattr(self, 'site_id', n.get_uuid_value()),
            "siteTitle": lambda n : setattr(self, 'site_title', n.get_str_value()),
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
        writer.write_uuid_value("actorId", self.actor_id)
        writer.write_str_value("actorName", self.actor_name)
        writer.write_uuid_value("platformId", self.platform_id)
        writer.write_str_value("platformKey", self.platform_key)
        writer.write_str_value("platformTitle", self.platform_title)
        writer.write_uuid_value("siteId", self.site_id)
        writer.write_str_value("siteTitle", self.site_title)
        writer.write_str_value("url", self.url)
        writer.write_additional_data_value(self.additional_data)
    

