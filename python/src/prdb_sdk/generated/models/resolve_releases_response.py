from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .release_resolution_result import ReleaseResolutionResult

@dataclass
class ResolveReleasesResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The evaluatedAtUtc property
    evaluated_at_utc: Optional[datetime.datetime] = None
    # The resolverVersion property
    resolver_version: Optional[str] = None
    # Exactly one result per input ref, in input order.
    results: Optional[list[ReleaseResolutionResult]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResolveReleasesResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResolveReleasesResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResolveReleasesResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .release_resolution_result import ReleaseResolutionResult

        from .release_resolution_result import ReleaseResolutionResult

        fields: dict[str, Callable[[Any], None]] = {
            "evaluatedAtUtc": lambda n : setattr(self, 'evaluated_at_utc', n.get_datetime_value()),
            "resolverVersion": lambda n : setattr(self, 'resolver_version', n.get_str_value()),
            "results": lambda n : setattr(self, 'results', n.get_collection_of_object_values(ReleaseResolutionResult)),
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
        writer.write_datetime_value("evaluatedAtUtc", self.evaluated_at_utc)
        writer.write_str_value("resolverVersion", self.resolver_version)
        writer.write_collection_of_object_values("results", self.results)
        writer.write_additional_data_value(self.additional_data)
    

