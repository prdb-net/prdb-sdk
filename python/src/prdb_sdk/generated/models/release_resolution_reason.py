from enum import Enum

class ReleaseResolutionReason(str, Enum):
    ConfirmedSource = "confirmedSource",
    CanonicalReleaseName = "canonicalReleaseName",
    HeuristicTitle = "heuristicTitle",
    NameCollision = "nameCollision",
    ContradictorySource = "contradictorySource",
    MissingOrigin = "missingOrigin",
    UnknownRelease = "unknownRelease",
    ExcludedReleaseKind = "excludedReleaseKind",
    DeletedTarget = "deletedTarget",
    IncompleteSource = "incompleteSource",
    BudgetExhausted = "budgetExhausted",
    InvalidField = "invalidField",
    UnverifiedSource = "unverifiedSource",
    AmbiguousSuccessor = "ambiguousSuccessor",
    WithdrawnAssociation = "withdrawnAssociation",
    UnsupportedPack = "unsupportedPack",

