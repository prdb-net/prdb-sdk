from enum import Enum

class GetSortByQueryParameterType(str, Enum):
    ReleaseDate = "releaseDate",
    Title = "title",

