from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .identify_video_file_dto import IdentifyVideoFileDto

@dataclass
class IdentifyVideosRequest(AdditionalDataHolder, Parsable):
    """
    Request body for identifying local files against the prdb catalogue.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Files to identify. Between 1 and 200 entries.
    files: Optional[list[IdentifyVideoFileDto]] = None
    # When true, each matched result carries the full video document. Defaults to false.
    include_video_details: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IdentifyVideosRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IdentifyVideosRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IdentifyVideosRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .identify_video_file_dto import IdentifyVideoFileDto

        from .identify_video_file_dto import IdentifyVideoFileDto

        fields: dict[str, Callable[[Any], None]] = {
            "files": lambda n : setattr(self, 'files', n.get_collection_of_object_values(IdentifyVideoFileDto)),
            "includeVideoDetails": lambda n : setattr(self, 'include_video_details', n.get_bool_value()),
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
        writer.write_collection_of_object_values("files", self.files)
        writer.write_bool_value("includeVideoDetails", self.include_video_details)
        writer.write_additional_data_value(self.additional_data)
    

