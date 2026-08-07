from enum import Enum

class GetCategoryQueryParameterType(str, Enum):
    Movies = "movies",
    Tvshows = "tvshows",
    Adult = "adult",

