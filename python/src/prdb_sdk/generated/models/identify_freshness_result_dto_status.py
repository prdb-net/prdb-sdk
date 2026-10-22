from enum import Enum

class IdentifyFreshnessResultDto_status(str, Enum):
    Unchanged = "unchanged",
    Identified = "identified",
    Reidentify = "reidentify",

