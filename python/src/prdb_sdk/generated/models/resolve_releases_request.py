from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resolve_release_input import ResolveReleaseInput

@dataclass
class ResolveReleasesRequest(AdditionalDataHolder, Parsable):
    """
    Local, read-only resolution of 1–200 release metadata records.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Release metadata, in the order results must be returned. Between 1 and 200 items.
    releases: Optional[list[ResolveReleaseInput]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResolveReleasesRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResolveReleasesRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResolveReleasesRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .resolve_release_input import ResolveReleaseInput

        from .resolve_release_input import ResolveReleaseInput

        fields: dict[str, Callable[[Any], None]] = {
            "releases": lambda n : setattr(self, 'releases', n.get_collection_of_object_values(ResolveReleaseInput)),
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
        writer.write_collection_of_object_values("releases", self.releases)
        writer.write_additional_data_value(self.additional_data)
    

