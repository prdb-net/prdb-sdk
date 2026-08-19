from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class AddWantedVideosBatchResponse(AdditionalDataHolder, Parsable):
    """
    Summary of a batch add-wanted-videos operation.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Number of entries newly added to the wanted list.
    added: Optional[int] = None
    # Number of entries that were already on the wanted list.
    already_existed: Optional[int] = None
    # Number of video IDs that were not found in the database.
    not_found: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AddWantedVideosBatchResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AddWantedVideosBatchResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AddWantedVideosBatchResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "added": lambda n : setattr(self, 'added', n.get_int_value()),
            "alreadyExisted": lambda n : setattr(self, 'already_existed', n.get_int_value()),
            "notFound": lambda n : setattr(self, 'not_found', n.get_int_value()),
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
        writer.write_int_value("added", self.added)
        writer.write_int_value("alreadyExisted", self.already_existed)
        writer.write_int_value("notFound", self.not_found)
        writer.write_additional_data_value(self.additional_data)
    

