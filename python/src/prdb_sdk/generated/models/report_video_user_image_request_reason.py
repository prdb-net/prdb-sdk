from enum import Enum

class ReportVideoUserImageRequest_reason(str, Enum):
    NotRelatedToVideo = "NotRelatedToVideo",
    SpamOrPromotional = "SpamOrPromotional",
    OffensiveOrProhibited = "OffensiveOrProhibited",
    DuplicateOrLowQuality = "DuplicateOrLowQuality",
    MisleadingOrWrongPreview = "MisleadingOrWrongPreview",
    CopyrightConcern = "CopyrightConcern",
    Other = "Other",

