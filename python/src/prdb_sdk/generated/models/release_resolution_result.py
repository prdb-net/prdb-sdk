from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .release_content_kind import ReleaseContentKind
    from .release_evidence_kind import ReleaseEvidenceKind
    from .release_resolution_reason import ReleaseResolutionReason
    from .release_resolution_status import ReleaseResolutionStatus
    from .release_resolution_warning import ReleaseResolutionWarning
    from .release_source_state import ReleaseSourceState
    from .resolved_release_video import ResolvedReleaseVideo

@dataclass
class ReleaseResolutionResult(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Identity is safe for automation; says nothing about rights, quality, availability or local ownership.
    automation_eligible: Optional[bool] = None
    # Alternative video identities, deterministically ordered, at most 20. Never pack membership.
    candidates: Optional[list[UUID]] = None
    # The candidatesTruncated property
    candidates_truncated: Optional[bool] = None
    # Known values: Single (0), Unknown (2).
    content_kind: Optional[ReleaseContentKind] = None
    # Public evidence categories only; never private source/person provenance.
    evidence: Optional[list[ReleaseEvidenceKind]] = None
    # Known values: ConfirmedSource (0), CanonicalReleaseName (1), HeuristicTitle (2), NameCollision (3), ContradictorySource (4), MissingOrigin (5), UnknownRelease (6), ExcludedReleaseKind (8), DeletedTarget (9), IncompleteSource (10), BudgetExhausted (11), InvalidField (12), UnverifiedSource (14), AmbiguousSuccessor (15), WithdrawnAssociation (16), UnsupportedPack (17).
    reason_code: Optional[ReleaseResolutionReason] = None
    # Earliest recommended automatic recheck; null only for permanent invalid/unsupported input.
    recheck_after_utc: Optional[datetime.datetime] = None
    # The ref property
    ref: Optional[str] = None
    # Opaque equality token for relevant input, association and catalogue facts; not a sortable feed cursor.
    resolution_version: Optional[str] = None
    # The sourceState property
    source_state: Optional[ReleaseSourceState] = None
    # Known values: Resolved (0), Candidate (1), Ambiguous (2), Unmatched (3), Conflict (4), Unsupported (5), RetryLater (6), Invalid (7).
    status: Optional[ReleaseResolutionStatus] = None
    # Confirmed active video IDs only. Empty unless resolved; a resolved result contains exactly one video.
    video_ids: Optional[list[UUID]] = None
    # The videos property
    videos: Optional[list[ResolvedReleaseVideo]] = None
    # The warnings property
    warnings: Optional[list[ReleaseResolutionWarning]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ReleaseResolutionResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ReleaseResolutionResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ReleaseResolutionResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .release_content_kind import ReleaseContentKind
        from .release_evidence_kind import ReleaseEvidenceKind
        from .release_resolution_reason import ReleaseResolutionReason
        from .release_resolution_status import ReleaseResolutionStatus
        from .release_resolution_warning import ReleaseResolutionWarning
        from .release_source_state import ReleaseSourceState
        from .resolved_release_video import ResolvedReleaseVideo

        from .release_content_kind import ReleaseContentKind
        from .release_evidence_kind import ReleaseEvidenceKind
        from .release_resolution_reason import ReleaseResolutionReason
        from .release_resolution_status import ReleaseResolutionStatus
        from .release_resolution_warning import ReleaseResolutionWarning
        from .release_source_state import ReleaseSourceState
        from .resolved_release_video import ResolvedReleaseVideo

        fields: dict[str, Callable[[Any], None]] = {
            "automationEligible": lambda n : setattr(self, 'automation_eligible', n.get_bool_value()),
            "candidates": lambda n : setattr(self, 'candidates', n.get_collection_of_primitive_values(UUID)),
            "candidatesTruncated": lambda n : setattr(self, 'candidates_truncated', n.get_bool_value()),
            "contentKind": lambda n : setattr(self, 'content_kind', n.get_enum_value(ReleaseContentKind)),
            "evidence": lambda n : setattr(self, 'evidence', n.get_collection_of_enum_values(ReleaseEvidenceKind)),
            "reasonCode": lambda n : setattr(self, 'reason_code', n.get_enum_value(ReleaseResolutionReason)),
            "recheckAfterUtc": lambda n : setattr(self, 'recheck_after_utc', n.get_datetime_value()),
            "ref": lambda n : setattr(self, 'ref', n.get_str_value()),
            "resolutionVersion": lambda n : setattr(self, 'resolution_version', n.get_str_value()),
            "sourceState": lambda n : setattr(self, 'source_state', n.get_object_value(ReleaseSourceState)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(ReleaseResolutionStatus)),
            "videoIds": lambda n : setattr(self, 'video_ids', n.get_collection_of_primitive_values(UUID)),
            "videos": lambda n : setattr(self, 'videos', n.get_collection_of_object_values(ResolvedReleaseVideo)),
            "warnings": lambda n : setattr(self, 'warnings', n.get_collection_of_enum_values(ReleaseResolutionWarning)),
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
        writer.write_bool_value("automationEligible", self.automation_eligible)
        writer.write_collection_of_primitive_values("candidates", self.candidates)
        writer.write_bool_value("candidatesTruncated", self.candidates_truncated)
        writer.write_enum_value("contentKind", self.content_kind)
        writer.write_collection_of_enum_values("evidence", self.evidence)
        writer.write_enum_value("reasonCode", self.reason_code)
        writer.write_datetime_value("recheckAfterUtc", self.recheck_after_utc)
        writer.write_str_value("ref", self.ref)
        writer.write_str_value("resolutionVersion", self.resolution_version)
        writer.write_object_value("sourceState", self.source_state)
        writer.write_enum_value("status", self.status)
        writer.write_collection_of_primitive_values("videoIds", self.video_ids)
        writer.write_collection_of_object_values("videos", self.videos)
        writer.write_collection_of_enum_values("warnings", self.warnings)
        writer.write_additional_data_value(self.additional_data)
    

