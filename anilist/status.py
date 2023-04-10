import enum


class MediaType(enum.Enum):
    MANGA = "MANGA"
    ANIME = "ANIME"


class PublishingStatus(enum.Enum):
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

    def decide_reading_status(self, id: int, publishing_status: PublishingStatus, progress: int, max_progress: int):
        if progress <= 0:
            return ReadingStatus.PLANNING

        if max_progress == None:
            return ReadingStatus.CURRENT

        if progress > max_progress:
            return ReadingStatus.COMPLETED

        if progress == max_progress and publishing_status == PublishingStatus.FINISHED:
            return ReadingStatus.COMPLETED

        return ReadingStatus.CURRENT
