from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resolve_release_source import ResolveReleaseSource

@dataclass
class ResolveReleaseInput(Parsable):
    """
    A release title and optional source hints. Never a file or a claimed video assignment.
    """
    # At most 20 origin-specific category hints, each at most 128 characters; never identity evidence.
    categories: Optional[list[str]] = None
    # UTC indexer/Usenet posting instant, not the video's release date.
    posted_at_utc: Optional[datetime.datetime] = None
    # Opaque caller correlation, 1–64 characters, unique within the batch; not identity evidence.
    ref: Optional[str] = None
    # Release size in bytes, a positive signed 64-bit integer; null means unknown.
    size_bytes: Optional[int] = None
    # The source property
    source: Optional[ResolveReleaseSource] = None
    # Original indexer release title, 1–2000 characters; not a local file path.
    title: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResolveReleaseInput:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResolveReleaseInput
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResolveReleaseInput()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .resolve_release_source import ResolveReleaseSource

        from .resolve_release_source import ResolveReleaseSource

        fields: dict[str, Callable[[Any], None]] = {
            "categories": lambda n : setattr(self, 'categories', n.get_collection_of_primitive_values(str)),
            "postedAtUtc": lambda n : setattr(self, 'posted_at_utc', n.get_datetime_value()),
            "ref": lambda n : setattr(self, 'ref', n.get_str_value()),
            "sizeBytes": lambda n : setattr(self, 'size_bytes', n.get_int_value()),
            "source": lambda n : setattr(self, 'source', n.get_object_value(ResolveReleaseSource)),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
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
        writer.write_collection_of_primitive_values("categories", self.categories)
        writer.write_datetime_value("postedAtUtc", self.posted_at_utc)
        writer.write_str_value("ref", self.ref)
        writer.write_int_value("sizeBytes", self.size_bytes)
        writer.write_object_value("source", self.source)
        writer.write_str_value("title", self.title)
    

