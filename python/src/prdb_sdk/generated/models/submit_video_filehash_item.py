from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class SubmitVideoFilehashItem(AdditionalDataHolder, Parsable):
    """
    A single hash-to-video assignment.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Channel count of the audio stream.
    audio_channels: Optional[int] = None
    # Codec of the audio stream, as the probe names it ("aac", "mp3").
    audio_codec: Optional[str] = None
    # Overall bit rate of the file in bits per second, across all streams.
    bit_rate: Optional[int] = None
    # Container of the file as the probe names it. Send it verbatim — it is usually a commaseparated list of the formats the demuxer covers ("mov,mp4,m4a,3gp,3g2,mj2"), not one token.
    container_format: Optional[str] = None
    # Duration of the file in milliseconds, if the client probed it. Optional, like every fieldbelow it: a client that cannot or will not probe submits without them.
    duration_ms: Optional[int] = None
    # File name without directory. Optional — a client may withhold it, and the endpoint works without it.
    filename: Optional[str] = None
    # Size of the file in bytes.
    filesize: Optional[int] = None
    # Average frame rate as the rational the probe reports, verbatim: "24000/1001", not "23.976".Rounding merges rates that are not the same one, and for a variable-rate file the largedenominator is the only sign that the value is an average rather than a rate.
    frame_rate: Optional[str] = None
    # Height of the video stream in pixels, as stored.
    height: Optional[int] = None
    # OS hash of the file, 16 hexadecimal characters. Required; it is the only aggregation key.
    os_hash: Optional[str] = None
    # Perceptual hash of the file, 16 hexadecimal characters, if the client computed one. It mustbe computed as "Perceptual hashes" in the API description prescribes; a submission carryinga value from another procedure contributes a row nothing can match.
    p_hash: Optional[str] = None
    # The scene release name the file came in, if the client knows one. Optional. It is a releasename, not a file name: send it when the acquisition carried one, and leave it out otherwise.
    release_name: Optional[str] = None
    # Known values: UserConfirmed (0), ClientDetected (1).
    source: Optional[int] = None
    # Codec of the video stream, as the probe names it ("h264", "hevc", "av1").
    video_codec: Optional[str] = None
    # The video this file is. Required — a hash observation without an assignment is not accepted.
    video_id: Optional[UUID] = None
    # Width of the video stream in pixels, as stored. Do not reorder it with the height to make the file landscape.
    width: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SubmitVideoFilehashItem:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SubmitVideoFilehashItem
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SubmitVideoFilehashItem()
    
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
            "durationMs": lambda n : setattr(self, 'duration_ms', n.get_int_value()),
            "filename": lambda n : setattr(self, 'filename', n.get_str_value()),
            "filesize": lambda n : setattr(self, 'filesize', n.get_int_value()),
            "frameRate": lambda n : setattr(self, 'frame_rate', n.get_str_value()),
            "height": lambda n : setattr(self, 'height', n.get_int_value()),
            "osHash": lambda n : setattr(self, 'os_hash', n.get_str_value()),
            "pHash": lambda n : setattr(self, 'p_hash', n.get_str_value()),
            "releaseName": lambda n : setattr(self, 'release_name', n.get_str_value()),
            "source": lambda n : setattr(self, 'source', n.get_int_value()),
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
        writer.write_int_value("durationMs", self.duration_ms)
        writer.write_str_value("filename", self.filename)
        writer.write_int_value("filesize", self.filesize)
        writer.write_str_value("frameRate", self.frame_rate)
        writer.write_int_value("height", self.height)
        writer.write_str_value("osHash", self.os_hash)
        writer.write_str_value("pHash", self.p_hash)
        writer.write_str_value("releaseName", self.release_name)
        writer.write_int_value("source", self.source)
        writer.write_str_value("videoCodec", self.video_codec)
        writer.write_uuid_value("videoId", self.video_id)
        writer.write_int_value("width", self.width)
        writer.write_additional_data_value(self.additional_data)
    

