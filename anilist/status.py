import enum
class AniListType(enum.Enum):
    manga = "MANGA"
    anime = "ANIME"


class MediaStatus(enum.Enum):
    HIATUS = "HIATUS"
    RELEASING = "RELEASING"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"  # NOT AN ANILIST STATUS


class ReadingStatus(enum.Enum):
    PLANNING = "PLANNING"
    COMPLETED = "COMPLETED"
    CURRENT = "CURRENT"
    DROPPED = "DROPPED"
    REPEATING = "REPEATING"
    PAUSED = "PAUSED"
    UNKNOWN = "UNKNOWN"  # NOT AN ANILIST STATUS
