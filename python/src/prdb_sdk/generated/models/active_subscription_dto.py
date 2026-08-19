from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ActiveSubscriptionDto(AdditionalDataHolder, Parsable):
    """
    An active subscription held by the authenticated user.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # UTC timestamp when this subscription period ends.
    ends_at_utc: Optional[datetime.datetime] = None
    # Stable slug identifying the subscription package (e.g. "plus", "premium").
    package_identifier: Optional[str] = None
    # Human-readable title of the subscription package.
    package_title: Optional[str] = None
    # UTC timestamp when this subscription period starts.
    starts_at_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ActiveSubscriptionDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ActiveSubscriptionDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ActiveSubscriptionDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "endsAtUtc": lambda n : setattr(self, 'ends_at_utc', n.get_datetime_value()),
            "packageIdentifier": lambda n : setattr(self, 'package_identifier', n.get_str_value()),
            "packageTitle": lambda n : setattr(self, 'package_title', n.get_str_value()),
            "startsAtUtc": lambda n : setattr(self, 'starts_at_utc', n.get_datetime_value()),
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
        writer.write_datetime_value("endsAtUtc", self.ends_at_utc)
        writer.write_str_value("packageIdentifier", self.package_identifier)
        writer.write_str_value("packageTitle", self.package_title)
        writer.write_datetime_value("startsAtUtc", self.starts_at_utc)
        writer.write_additional_data_value(self.additional_data)
    

