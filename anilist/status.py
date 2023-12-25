from dataclasses import dataclass
import enum
from typing import List, dataclass_transform


class MediaType(enum.Enum):
    MANGA = "MANGA"
    ANIME = "ANIME"


class MediaSeason(enum.Enum):
    WINTER = "WINTER"
    FALL = "FALL"
    SUMMER = "SUMMER"
    SPRING = "SPRING"
    UNKNOWN = "UNKNOWN"


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

    @classmethod
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

@dataclass
class AniManga:
    id :int
    synonyms :list
    ani_type :str
    title :dict
    start_date :dict
    end_date :dict
    cover_image :dict
    tags :list
    is_adult :bool
    banner_image :str
    format :str
    chapters :int
    volumes :int
    status :PublishingStatus
    description :str
    average_score :int
    mean_score :int
    genres :list

@dataclass
class AniAnime:
    id :int
    synonyms :list
    type :str
    title :dict
    start_date :dict
    end_date :dict
    cover_image :dict
    tags :list
    is_adult :bool
    banner_image :str
    format :str
    episodes :int
    status :PublishingStatus
    description :str
    average_score :int
    mean_score :int
    genres :list

@dataclass
class AniUser:
    id: str
    name: str
    avatar_url: str
    site_url :str
    previousNames :dict
    anime_statistics :dict
    manga_statistics :dict

@dataclass
class AniUserMangaEntry: # TODO: rename it
    entry_id :int
    manga_id :int # doppelt gemoppelt?
    repeat :int 
    progress :int
    notes :str
    info :AniManga
