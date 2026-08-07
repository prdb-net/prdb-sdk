from enum import Enum

class GetSortByQueryParameterType(str, Enum):
    Title = "title",
    ReleaseDate = "releaseDate",
    CreatedAtUtc = "createdAtUtc",

