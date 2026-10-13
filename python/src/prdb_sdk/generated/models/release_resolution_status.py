from enum import Enum

class ReleaseResolutionStatus(str, Enum):
    Resolved = "resolved",
    Candidate = "candidate",
    Ambiguous = "ambiguous",
    Unmatched = "unmatched",
    Conflict = "conflict",
    Unsupported = "unsupported",
    RetryLater = "retryLater",
    Invalid = "invalid",

