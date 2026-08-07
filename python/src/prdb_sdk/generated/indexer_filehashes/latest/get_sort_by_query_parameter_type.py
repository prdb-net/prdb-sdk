from enum import Enum

class GetSortByQueryParameterType(str, Enum):
    CreatedAtUtc = "createdAtUtc",
    UpdatedAtUtc = "updatedAtUtc",
    SubmissionCount = "submissionCount",
    Filesize = "filesize",

