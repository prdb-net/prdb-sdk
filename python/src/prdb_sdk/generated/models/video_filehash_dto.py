from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class VideoFilehashDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Channel count of the audio stream.
    audio_channels: Optional[int] = None
    # Codec of the audio stream, lower-cased ("aac", "mp3").
    audio_codec: Optional[str] = None
    # Overall bit rate in bits per second, across all streams.
    bit_rate: Optional[int] = None
    # Container as the probe names it. Usually a comma separated list of the formats one demuxer covers ("mov,mp4,m4a,3gp,3g2,mj2"), not a single token.
    container_format: Optional[str] = None
    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # Duration of this file in milliseconds, as the submitting clients probed it, or null when none reported one.
    duration_ms: Optional[int] = None
    # Original filename submitted for this filehash record.
    filename: Optional[str] = None
    # File size in bytes.
    filesize: Optional[int] = None
    # Average frame rate as a rational, exactly as it was measured: "24000/1001", never a roundeddecimal. Rounding merges rates that are not the same one, and a variable-rate file carries aper-file average whose large denominator is what marks it as variable rather than as a rate.
    frame_rate: Optional[str] = None
    # Height of the video stream in pixels, as stored.
    height: Optional[int] = None
    # The id property
    id: Optional[UUID] = None
    # Whether this filehash record has been verified.
    is_verified: Optional[bool] = None
    # OS hash value as stored, or null when not available.
    os_hash: Optional[str] = None
    # P hash value as stored, or null when not available.
    p_hash: Optional[str] = None
    # Number of submissions merged into this filehash record.
    submission_count: Optional[int] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    # Codec of the video stream, lower-cased ("h264", "hevc", "av1").
    video_codec: Optional[str] = None
    # The videoId property
    video_id: Optional[UUID] = None
    # Width of the video stream in pixels, as stored. Not necessarily the larger dimension: portrait video is ordinary.
    width: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VideoFilehashDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VideoFilehashDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VideoFilehashDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "audioChannels": lambda n : setattr(self, 'audio_channels', n.get_int_value()),
            "audioCodec": lambda n : setattr(self, 'audio_codec', n.get_str_value()),
            "bitRate": lambda n : setattr(self, 'bit_rate', n.get_int_value()),
            "containerFormat": lambda n : setattr(self, 'container_format', n.get_str_value()),
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "durationMs": lambda n : setattr(self, 'duration_ms', n.get_int_value()),
            "filename": lambda n : setattr(self, 'filename', n.get_str_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "frameRate": lambda n : setattr(self, 'frame_rate', n.get_str_value()),
            "height": lambda n : setattr(self, 'height', n.get_int_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "isVerified": lambda n : setattr(self, 'is_verified', n.get_bool_value()),
            "osHash": lambda n : setattr(self, 'os_hash', n.get_str_value()),
            "pHash": lambda n : setattr(self, 'p_hash', n.get_str_value()),
            "submissionCount": lambda n : setattr(self, 'submission_count', n.get_int_value()),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
            "videoCodec": lambda n : setattr(self, 'video_codec', n.get_str_value()),
            "videoId": lambda n : setattr(self, 'video_id', n.get_uuid_value()),
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
        writer.write_int_value("audioChannels", self.audio_channels)
        writer.write_str_value("audioCodec", self.audio_codec)
        writer.write_int_value("bitRate", self.bit_rate)
        writer.write_str_value("containerFormat", self.container_format)
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_int_value("durationMs", self.duration_ms)
        writer.write_str_value("filename", self.filename)
        writer.write_int_value("filesize", self.filesize)
        writer.write_str_value("frameRate", self.frame_rate)
        writer.write_int_value("height", self.height)
        writer.write_uuid_value("id", self.id)
        writer.write_bool_value("isVerified", self.is_verified)
        writer.write_str_value("osHash", self.os_hash)
        writer.write_str_value("pHash", self.p_hash)
        writer.write_int_value("submissionCount", self.submission_count)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_str_value("videoCodec", self.video_codec)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_int_value("width", self.width)
        writer.write_additional_data_value(self.additional_data)
    

