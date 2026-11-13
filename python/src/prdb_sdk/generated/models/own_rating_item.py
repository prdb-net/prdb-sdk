from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .own_rating_review import OwnRatingReview
    from .rating_target_type import RatingTargetType

@dataclass
class OwnRatingItem(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The createdAtUtc property
    created_at_utc: Optional[datetime.datetime] = None
    # The id property
    id: Optional[UUID] = None
    # The review property
    review: Optional[OwnRatingReview] = None
    # The stars property
    stars: Optional[int] = None
    # The targetId property
    target_id: Optional[UUID] = None
    # The targetTitle property
    target_title: Optional[str] = None
    # Known values: Video (1), Actor (2).
    target_type: Optional[RatingTargetType] = None
    # The updatedAtUtc property
    updated_at_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OwnRatingItem:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OwnRatingItem
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OwnRatingItem()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .own_rating_review import OwnRatingReview
        from .rating_target_type import RatingTargetType

        from .own_rating_review import OwnRatingReview
        from .rating_target_type import RatingTargetType

        fields: dict[str, Callable[[Any], None]] = {
            "createdAtUtc": lambda n : setattr(self, 'created_at_utc', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_uuid_value()),
            "review": lambda n : setattr(self, 'review', n.get_object_value(OwnRatingReview)),
            "stars": lambda n : setattr(self, 'stars', n.get_int_value()),
            "targetId": lambda n : setattr(self, 'target_id', n.get_uuid_value()),
            "targetTitle": lambda n : setattr(self, 'target_title', n.get_str_value()),
            "targetType": lambda n : setattr(self, 'target_type', n.get_enum_value(RatingTargetType)),
            "updatedAtUtc": lambda n : setattr(self, 'updated_at_utc', n.get_datetime_value()),
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
        writer.write_datetime_value("createdAtUtc", self.created_at_utc)
        writer.write_uuid_value("id", self.id)
        writer.write_object_value("review", self.review)
        writer.write_int_value("stars", self.stars)
        writer.write_uuid_value("targetId", self.target_id)
        writer.write_str_value("targetTitle", self.target_title)
        writer.write_enum_value("targetType", self.target_type)
        writer.write_datetime_value("updatedAtUtc", self.updated_at_utc)
        writer.write_additional_data_value(self.additional_data)
    

