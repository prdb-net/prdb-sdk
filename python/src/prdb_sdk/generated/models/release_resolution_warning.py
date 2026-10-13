from enum import Enum

class ReleaseResolutionWarning(str, Enum):
    UnverifiedSource = "unverifiedSource",
    SourceStale = "sourceStale",
    CreditsIncomplete = "creditsIncomplete",
    CandidatesTruncated = "candidatesTruncated",

