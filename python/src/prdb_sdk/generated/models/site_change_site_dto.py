from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .site_change_link_dto import SiteChangeLinkDto

@dataclass
class SiteChangeSiteDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Public account handle, independent of the local Site UUID.
    account_handle: Optional[str] = None
    # When this site was created.
    created_at_utc: Optional[datetime.datetime] = None
    # The deletedAtUtc property
    deleted_at_utc: Optional[datetime.datetime] = None
    # Unique identifier of the site.
    id: Optional[UUID] = None
    # The isDeleted property
    is_deleted: Optional[bool] = None
    # Additional catalogue links. Provenance is intentionally not part of this contract.
    links: Optional[list[SiteChangeLinkDto]] = None
    # Unique identifier of the network this site belongs to, if any.
    network_id: Optional[UUID] = None
    # Title of the network this site belongs to, if any.
    network_title: Optional[str] = None
    # The networkUrl property
    network_url: Optional[str] = None
    # Publishing platform UUID; null for classic studio sites.
    platform_id: Optional[UUID] = None
    # Stable publishing platform key; null for classic sites.
    platform_key: Optional[str] = None
    # Publishing platform display title; null for classic sites.
    platform_title: Optional[str] = None
    # Site title.
    title: Optional[str] = None
    # When this site was last changed.
    updated_at_utc: Optional[datetime.datetime] = None
    # Site URL.
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SiteChangeSiteDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SiteChangeSiteDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SiteChangeSiteDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .site_change_link_dto import SiteChangeLinkDto

        from .site_change_link_dto import SiteChangeLinkDto

        fields: dict[str, Callable[[Any], None]] = {
            "accountHandle": lambda n : setattr(self, 'account_handle', n.get_str_value()),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "deletedAtUtc": lambda n : setattr(self, 'deleted_at_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "isDeleted": lambda n : setattr(self, 'is_deleted', n.get_bool_value()),
            "links": lambda n : setattr(self, 'links', n.get_collection_of_object_values(SiteChangeLinkDto)),
            "networkId": lambda n : setattr(self, 'network_id', n.get_uuid_value()),
            "networkTitle": lambda n : setattr(self, 'network_title', n.get_str_value()),
            "networkUrl": lambda n : setattr(self, 'network_url', n.get_str_value()),
            "platformId": lambda n : setattr(self, 'platform_id', n.get_uuid_value()),
            "platformKey": lambda n : setattr(self, 'platform_key', n.get_str_value()),
            "platformTitle": lambda n : setattr(self, 'platform_title', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
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
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_datetime_value("deletedAtUtc", self.deleted_at_utc)
        writer.write_uuid_value("id", self.id)
        writer.write_bool_value("isDeleted", self.is_deleted)
        writer.write_collection_of_object_values("links", self.links)
        writer.write_uuid_value("networkId", self.network_id)
        writer.write_str_value("networkTitle", self.network_title)
        writer.write_str_value("networkUrl", self.network_url)
        writer.write_uuid_value("platformId", self.platform_id)
        writer.write_str_value("platformKey", self.platform_key)
        writer.write_str_value("platformTitle", self.platform_title)
        writer.write_str_value("title", self.title)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_str_value("url", self.url)
        writer.write_additional_data_value(self.additional_data)
    

