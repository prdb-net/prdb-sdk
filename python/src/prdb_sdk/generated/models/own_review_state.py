from enum import Enum

class OwnReviewState(str, Enum):
    None_ = "None",
    Published = "Published",
    Pending = "Pending",
    Rejected = "Rejected",
    Hidden = "Hidden",

