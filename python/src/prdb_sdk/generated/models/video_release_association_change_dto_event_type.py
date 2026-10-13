from enum import Enum

class VideoReleaseAssociationChangeDto_eventType(str, Enum):
    Created = "created",
    Updated = "updated",
    Deleted = "deleted",

