from enum import Enum

class ReleaseSourceFreshness(str, Enum):
    Current = "current",
    Stale = "stale",
    Unknown = "unknown",
    NotApplicable = "notApplicable",

