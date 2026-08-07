from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class VideoUserImageDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The basedOnFileWithOsHash property
    based_on_file_with_os_hash: Optional[str] = None
    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The deletedAtUtc property
    deleted_at_utc: Optional[datetime.datetime] = None
    # The displayOrder property
    display_order: Optional[int] = None
    # The filesize property
    filesize: Optional[int] = None
    # The hasVtt property
    has_vtt: Optional[bool] = None
    # The height property
    height: Optional[int] = None
    # The id property
    id: Optional[UUID] = None
    # The isDeleted property
    is_deleted: Optional[bool] = None
    # The moderationStatus property
    moderation_status: Optional[str] = None
    # The moderationVisibility property
    moderation_visibility: Optional[str] = None
    # The previewImageType property
    preview_image_type: Optional[str] = None
    # The spriteColumns property
    sprite_columns: Optional[int] = None
    # The spriteRows property
    sprite_rows: Optional[int] = None
    # The spriteTileCount property
    sprite_tile_count: Optional[int] = None
    # The spriteTileHeight property
    sprite_tile_height: Optional[int] = None
    # The spriteTileWidth property
    sprite_tile_width: Optional[int] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    # The url property
    url: Optional[str] = None
    # The userId property
    user_id: Optional[UUID] = None
    # The videoId property
    video_id: Optional[UUID] = None
    # The vttUrl property
    vtt_url: Optional[str] = None
    # The width property
    width: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoUserImageDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoUserImageDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoUserImageDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "basedOnFileWithOsHash": lambda n : setattr(self, 'based_on_file_with_os_hash', n.get_str_value()),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "deletedAtUtc": lambda n : setattr(self, 'deleted_at_utc', n.get_datetime_value()),
            "displayOrder": lambda n : setattr(self, 'display_order', n.get_int_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "hasVtt": lambda n : setattr(self, 'has_vtt', n.get_bool_value()),
            "height": lambda n : setattr(self, 'height', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "isDeleted": lambda n : setattr(self, 'is_deleted', n.get_bool_value()),
            "moderationStatus": lambda n : setattr(self, 'moderation_status', n.get_str_value()),
            "moderationVisibility": lambda n : setattr(self, 'moderation_visibility', n.get_str_value()),
            "previewImageType": lambda n : setattr(self, 'preview_image_type', n.get_str_value()),
            "spriteColumns": lambda n : setattr(self, 'sprite_columns', n.get_int_value()),
            "spriteRows": lambda n : setattr(self, 'sprite_rows', n.get_int_value()),
            "spriteTileCount": lambda n : setattr(self, 'sprite_tile_count', n.get_int_value()),
            "spriteTileHeight": lambda n : setattr(self, 'sprite_tile_height', n.get_int_value()),
            "spriteTileWidth": lambda n : setattr(self, 'sprite_tile_width', n.get_int_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
            "url": lambda n : setattr(self, 'url', n.get_str_value()),
            "userId": lambda n : setattr(self, 'user_id', n.get_uuid_value()),
            "videoId": lambda n : setattr(self, 'video_id', n.get_uuid_value()),
            "vttUrl": lambda n : setattr(self, 'vtt_url', n.get_str_value()),
            "width": lambda n : setattr(self, 'width', n.get_int_value()),
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
        writer.write_str_value("basedOnFileWithOsHash", self.based_on_file_with_os_hash)
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_datetime_value("deletedAtUtc", self.deleted_at_utc)
        writer.write_int_value("displayOrder", self.display_order)
        writer.write_int_value("filesize", self.filesize)
        writer.write_bool_value("hasVtt", self.has_vtt)
        writer.write_int_value("height", self.height)
        writer.write_uuid_value("id", self.id)
        writer.write_bool_value("isDeleted", self.is_deleted)
        writer.write_str_value("moderationStatus", self.moderation_status)
        writer.write_str_value("moderationVisibility", self.moderation_visibility)
        writer.write_str_value("previewImageType", self.preview_image_type)
        writer.write_int_value("spriteColumns", self.sprite_columns)
        writer.write_int_value("spriteRows", self.sprite_rows)
        writer.write_int_value("spriteTileCount", self.sprite_tile_count)
        writer.write_int_value("spriteTileHeight", self.sprite_tile_height)
        writer.write_int_value("spriteTileWidth", self.sprite_tile_width)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_str_value("url", self.url)
        writer.write_uuid_value("userId", self.user_id)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_str_value("vttUrl", self.vtt_url)
        writer.write_int_value("width", self.width)
        writer.write_additional_data_value(self.additional_data)
    

