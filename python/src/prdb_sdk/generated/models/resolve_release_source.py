from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .release_source_kind import ReleaseSourceKind

@dataclass
class ResolveReleaseSource(Parsable):
    # Opaque, case-sensitive provider key (max 512 characters); a central entry UUID for nzbcache.
    entry_id: Optional[str] = None
    # Known values: Newznab (0), Nzbcache (1).
    kind: Optional[ReleaseSourceKind] = None
    # HTTPS service origin with optional stable base path; no userinfo, query or fragment. Never fetched.
    origin: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResolveReleaseSource:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResolveReleaseSource
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResolveReleaseSource()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .release_source_kind import ReleaseSourceKind

        from .release_source_kind import ReleaseSourceKind

        fields: dict[str, Callable[[Any], None]] = {
            "entryId": lambda n : setattr(self, 'entry_id', n.get_str_value()),
            "kind": lambda n : setattr(self, 'kind', n.get_enum_value(ReleaseSourceKind)),
            "origin": lambda n : setattr(self, 'origin', n.get_str_value()),
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
        writer.write_str_value("entryId", self.entry_id)
        writer.write_enum_value("kind", self.kind)
        writer.write_str_value("origin", self.origin)
    

