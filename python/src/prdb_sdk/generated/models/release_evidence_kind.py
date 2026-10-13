from enum import Enum

class ReleaseEvidenceKind(str, Enum):
    ConfirmedEntryAssociation = "confirmedEntryAssociation",
    CanonicalReleaseAssociation = "canonicalReleaseAssociation",
    HeuristicTitle = "heuristicTitle",

