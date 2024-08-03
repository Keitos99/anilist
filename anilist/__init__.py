from http import HTTPStatus
from time import sleep

import requests

from anilist import queries as graphql
from anilist.status import (
    AniAnime,
    AniManga,
    AniUser,
    AniUserMangaEntry,
    MediaType,
    PublishingStatus,
    ReadingStatus,
)
from anilist.tools import find_matching_media

TIMEOUT_IN_SECONDS = 5
RETRY_IN_SECONDS = 60


def _run_query(url, query, variables, headers=None, expected_status_code=HTTPStatus.OK):
    response = requests.post(
        url,
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=TIMEOUT_IN_SECONDS,
    )
    if response.status_code == expected_status_code:
        return response.json()
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        # HACK: to many request so waiting before retrying
        print(
            f"To many request to {url}. Retrying after a {RETRY_IN_SECONDS} seconds..."
        )
        sleep(RETRY_IN_SECONDS)
        return _run_query(
            url=url,
            query=query,
            variables=variables,
            headers=headers,
            expected_status_code=expected_status_code,
        )
    else:
        # TODO: maybe it should retry it until it work?
        raise Exception(
            f"Unexpected status code {response.status_code} was returned from the server.\n"
            + f"Query: {query}\n"
            + f"variables: {variables}\n"
            + f"response text: {response.text}\n"
        )


class Anilist:
    URI = "https://graphql.anilist.co"

    # based of https://anilist.github.io/ApiV2-GraphQL-Docs/
    def __init__(self, authorization: str = ""):
        """
        authorization must only be set, if you want to change something on anilist
        """
        if not authorization:
            self.header = None
            return

        CONTENT_TYP = "application/json"
        ACCEPT = "application/json"
        self.header = {
            "Authorization": authorization,
            "Content-Type": CONTENT_TYP,
            "Accept": ACCEPT,
        }

    def search_manga(self, search_query: str = "", media_id: int = 0) -> AniManga:
        variables = {}
        if media_id > 0:
            variables["id"] = media_id
        else:
            variables["search"] = search_query

        response = _run_query(
            url=self.URI,
            query=graphql.SEARCH_MANGA,
            variables=variables,
            headers=self.header,
        )
        medias = response["data"]["Page"]["media"]
        page = response["data"]["Page"]
        total = page["pageInfo"]["total"]
        if total == 0:
            return None

        medias = page["media"]
        media = {}
        if media_id > 0:
            media = medias[0]
        else:
            media = find_matching_media(search_query, medias)

        if not media:
            return None

        return AniManga(
            id=media["id"],
            synonyms=media["synonyms"],
            ani_type=MediaType(media["type"]),
            title=media["title"],
            start_date=media["startDate"],
            end_date=media["endDate"],
            cover_image=media["coverImage"]["large"],
            tags=media["tags"],
            is_adult=media["isAdult"],
            banner_image=media["bannerImage"],
            format=media["format"],
            chapters=media["chapters"],
            volumes=media["volumes"],
            status=PublishingStatus(media["status"]),
            description=media["description"],
            average_score=media["averageScore"],
            mean_score=media["meanScore"],
            genres=media["genres"],
        )

    def search_anime(self, search_query: str = "", media_id: int = 0) -> AniAnime:
        variables = {}
        if media_id > 0:
            variables["id"] = media_id
        else:
            variables["search"] = search_query

        response = _run_query(
            url=self.URI,
            query=graphql.SEARCH_ANIME,
            variables=variables,
            headers=self.header,
        )
        medias = response["data"]["Page"]["media"]
        page = response["data"]["Page"]
        total = page["pageInfo"]["total"]
        if total == 0:
            return None

        medias = page["media"]
        media = {}
        if media_id > 0:
            media = medias[0]
        else:
            media = find_matching_media(search_query, medias)
        if not media:
            return None

        return AniAnime(
            id=media["id"],
            synonyms=media["synonyms"],
            type=media["type"],
            title=media["title"],
            start_date=media["startDate"],
            end_date=media["endDate"],
            cover_image=media["coverImage"],
            tags=media["tags"],
            is_adult=media["isAdult"],
            banner_image=media["bannerImage"],
            format=media["format"],
            episodes=media["episodes"],
            status=PublishingStatus(media["status"]),
            description=media["description"],
            average_score=media["averageScore"],
            mean_score=media["meanScore"],
            genres=media["genres"],
        )

    def search_user(self, user_name: str) -> AniUser:
        variables = {"search": user_name, "sort": "USERNAME"}
        result = _run_query(
            url=self.URI, query=graphql.SEARCH_USER_QUERY, variables=variables
        )

        users = result["data"]["Page"]["users"]
        for user in users:
            if user["name"] == user_name:
                return AniUser(
                    id=user["id"],
                    name=user["name"],
                    avatar_url=user["avatar"]["large"],
                    site_url=user["siteUrl"],
                    previousNames=user["previousNames"],
                    anime_statistics=user["statistics"]["anime"],
                    manga_statistics=user["statistics"]["manga"],
                )
        return None

    def get_user_manga_collection(self, user_name: str = "") -> list[AniUserMangaEntry]:
        user = self.search_user(user_name=user_name)
        if not user:
            return None

        variables = {"userId": user.id}
        response = _run_query(
            self.URI,
            query=graphql.MANGA_LIST_COLLECTION_QUERY,
            headers=self.header,
            variables=variables,
        )

        mangas: list[AniUserMangaEntry] = []
        entries = response["data"]["MediaListCollection"]["lists"][0]["entries"]
        for entry in entries:
            media = entry["media"]
            mangas.append(
                AniUserMangaEntry(
                    entry_id=entry["id"],
                    manga_id=media["id"],
                    repeat=entry["repeat"],
                    progress=entry["progress"],
                    notes=entry["notes"],
                    reading_status=entry["status"],
                    info=AniManga(
                        id=media["id"],
                        synonyms=media["synonyms"],
                        ani_type=MediaType(media["type"]),
                        title=media["title"],
                        start_date=media["startDate"],
                        end_date=media["endDate"],
                        cover_image=media["coverImage"]["large"],
                        tags=media["tags"],
                        is_adult=media["isAdult"],
                        banner_image=media["bannerImage"],
                        format=media["format"],
                        chapters=media["chapters"],
                        volumes=media["volumes"],
                        status=PublishingStatus(media["status"]),
                        description=media["description"],
                        average_score=media["averageScore"],
                        mean_score=media["meanScore"],
                        genres=media["genres"],
                    ),
                )
            )

        return mangas

    def update_progress(
        self, media_id: int, progress: int, reading_status: ReadingStatus = None
    ) -> bool:
        """
        Attention: if it is an anime reading_status must be set
        """
        if media_id < 0:
            raise Exception(f"id={media_id} must be positive")

        if progress < 0:
            raise Exception(f"progress={progress} must be positive")

        if not reading_status:
            manga = self.search_manga(media_id=media_id)
            max_progress = manga.chapters
            publishing_status = manga.status
            reading_status = ReadingStatus.decide_reading_status(
                media_id, publishing_status, progress, max_progress
            )

        variables = {
            "mediaId": media_id,
            "status": reading_status.value,
            "progress": progress,
        }
        response = _run_query(
            self.URI,
            query=graphql.MEDIA_PROGRESS_MUTATION,
            headers=self.header,
            variables=variables,
        )

        save_media_list = response["data"]["SaveMediaListEntry"]
        saved_reading_status = ReadingStatus(save_media_list["status"])
        return (
            progress == save_media_list["progress"]
            or saved_reading_status == reading_status
        )
