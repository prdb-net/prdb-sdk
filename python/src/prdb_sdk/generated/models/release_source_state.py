from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .release_source_freshness import ReleaseSourceFreshness

@dataclass
class ReleaseSourceState(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The lastSuccessfulSyncAtUtc property
    last_successful_sync_at_utc: Optional[datetime.datetime] = None
    # Known values: Current (0), Stale (1), Unknown (2), NotApplicable (3).
    state: Optional[ReleaseSourceFreshness] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ReleaseSourceState:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ReleaseSourceState
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ReleaseSourceState()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .release_source_freshness import ReleaseSourceFreshness

        from .release_source_freshness import ReleaseSourceFreshness

        fields: dict[str, Callable[[Any], None]] = {
            "lastSuccessfulSyncAtUtc": lambda n : setattr(self, 'last_successful_sync_at_utc', n.get_datetime_value()),
            "state": lambda n : setattr(self, 'state', n.get_enum_value(ReleaseSourceFreshness)),
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
        writer.write_datetime_value("lastSuccessfulSyncAtUtc", self.last_successful_sync_at_utc)
        writer.write_enum_value("state", self.state)
        writer.write_additional_data_value(self.additional_data)
    

