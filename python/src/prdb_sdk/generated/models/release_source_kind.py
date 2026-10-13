from enum import Enum

class ReleaseSourceKind(str, Enum):
    Newznab = "newznab",
    Nzbcache = "nzbcache",

