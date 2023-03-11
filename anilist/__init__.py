import enum
from http import HTTPStatus
from os import error, ttyname, wait
import os
import shutil
from time import sleep
from typing import Dict, List, Tuple

import requests
from requests.sessions import Request

from anilist import queries as graphql
from anilist.database import Database
from anilist.status import AniListType, MediaStatus, ReadingStatus
from anilist.tools import get_matching_media, get_matching_title


# based on https://anilist.github.io/ApiV2-GraphQL-Docs/
class Anilist:
    URI = "https://graphql.anilist.co"
    CONTENT_TYP = "application/json"
    ACCEPT = "application/json"

    def __init__(self, authorization: str = "", database=Database()):
        self.database = database

        if not authorization:
            return

        self.header = {
            "Authorization": authorization,
            "Content-Type": self.CONTENT_TYP,
            "Accept": self.ACCEPT,
        }

    def update_progress(self, id: int, progress: int):
        if not self.header:
            raise Exception("You must add your anilist token to update entries")

        if id < 0:
            raise Exception("id={} must be positive".format(id))

        if progress < 0:
            raise Exception("progress={} must be positive".format(progress))

        try:
            query = graphql.UPDATE_QUERY
            variables = {
                "mediaId": id,
                "status": self.decide_reading_status(id, progress).value,
                "progress": progress,
            }
            response = _run_query(
                self.URI, query=query, headers=self.header, variables=variables
            )
        except Exception as e:
            print(e)
            return False

        return True

    def _search(self, type: AniListType, search_query: str) -> Dict:
        search_query = search_query.replace("\n", "")
        title = None
        id = -1

        id = self.database.get_id(search_query, type)
        if id > 0:  # was once searched, so choosing the correct one can be skipped
            return _run_query(
                self.URI,
                query=graphql.SEARCH_QUERY_ID,
                variables={"id": id, "typ": type.value},
            )

        query = graphql.SEARCH_QUERY
        variables = {
            "search": search_query,
            "type": type.value,
        }

        response = _run_query(
            self.URI,
            query=query,
            variables=variables,
        )
        page = response["data"]["Page"]
        total = page["pageInfo"]["total"]
        medias = page["media"]

        if total == 0:
            return None

        media = get_matching_media(search_query, medias)

        if media:
            self.database.save_media(search_query, media)
            return media

        # TODO: not sure if this is the right approach
        # HACK: falling back to the first media
        media = page["media"][0]
        return media

    def search_manga(self, search_query: str) -> Dict:
        return self._search(AniListType.manga, search_query)

    def search_anime(self, search_query: str) -> Dict:
        return self._search(AniListType.anime, search_query)

    def get_manga_title(self, search_query: str) -> int:
        title = self.database.get_title(search_query, AniListType.manga)
        if title:
            return title

        manga = self.search_manga(search_query=search_query)
        if not manga:
            return ""

        self.database.save_media(search_query, manga)
        titles = list(manga["title"].values()) + manga["synonyms"]
        return get_matching_title(search_query, titles)

    def get_manga_id(self, search_query: str) -> int:
        id = self.database.get_id(search_query, AniListType.manga)
        if id > 0:
            return id

        manga = self.search_manga(search_query=search_query)
        if not manga:
            return -1

        self.database.save_media(search_query, manga)
        return manga["id"]

    def decide_reading_status(self, id: int, progress: int) -> ReadingStatus:
        if progress <= 0:
            return ReadingStatus.PLANNING

        query = graphql.READING_STATUS
        variables = {"id": id, "page": 1, "perPage": 100}
        response = _run_query(self.URI, query=query, variables=variables)
        medias = response["data"]["Page"]["media"]

        if len(medias) == 0:
            raise Exception("No matches")

        media = medias[0]
        max_progress = (
            media["chapters"] if media["chapters"] != None else media["episodes"]
        )

        if max_progress == None:
            return ReadingStatus.CURRENT

        if progress > max_progress:
            # print("Anilist::reading_status -> Anilistid={}: You have read {}, but only {} exists".format( id, progress, max_progress))
            return ReadingStatus.COMPLETED

        if progress == max_progress and media["status"] == "FINISHED":
            return ReadingStatus.COMPLETED

        return ReadingStatus.CURRENT

    def get_cover_image(self, id: int) -> str:
        variables = {"id": id, "page": 1, "perPage": 1, "type": AniListType.manga.value}
        return _run_query(
            uri=self.URI,
            query=graphql.SEARCH_IMAGES,
            variables=variables,
        )["data"]["Page"]["media"][0]["coverImage"]["medium"]

    def search_user(self, user_name: str):
        variables = {"search": user_name, "sort": "USERNAME"}
        result = _run_query(
            uri=self.URI, query=graphql.SEARCH_USER, variables=variables
        )

        users = result["data"]["Page"]["users"]
        for user in users:
            if user["name"] == user_name:
                return user
        return None

    def get_manga_collection_of(self, user_name: str) -> Dict:
        user = self.search_user(user_name)
        if not user:
            return {}

        manga_list_collection = self.get_manga_collection_of(user["id"])
        lists = manga_list_collection["lists"]

        mangas = {}
        for list in lists:
            entries = list["entries"]
            for entry in entries:
                reading_status = ReadingStatus[entry["status"]]
                media = entry["media"]
                id = media["id"]
                title = media["title"]
                media_status = MediaStatus(media["status"])
                max_chapters = media["chapters"]
                genres = media["genres"]
                tags = [tag["name"] for tag in media["tags"]]
                if max_chapters == None:
                    max_chapters = 0

                mangas[id] = entry
                mangas[id]["title"] = title
                mangas[id]["status"] = reading_status
                mangas[id]["media_status"] = media_status
                mangas[id]["chapters"] = max_chapters
                mangas[id]["genres"] = genres
                mangas[id]["tags"] = tags
        return mangas

    def get_manga_collection_of(self, user_id: int):
        variables = {"userId": user_id}
        result = _run_query(
            uri=self.URI, query=graphql.MANGA_LIST_COLLECTION, variables=variables
        )
        return result["data"]["MediaListCollection"]


def _run_query(uri, query, variables, headers=None, expected_status_code=HTTPStatus.OK):
    response = requests.post(
        uri, json={"query": query, "variables": variables}, headers=headers
    )
    if response.status_code == expected_status_code:
        return response.json()
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        # HACK: to many request so waiting before retrying
        sleep(60)
        return _run_query(
            uri=uri,
            query=query,
            variables=variables,
            headers=headers,
            expected_status_code=expected_status_code,
        )
    else:
        # TODO: maybe it should retry it until it work?
        print("run_query:: Query:", query)
        print("run_query:: variables", variables)
        print("run_query:: variables", response.text)
        raise Exception(f"Unexpected status code returned: {response.status_code}")


if __name__ == "__main__":
    token = os.environ["ANILIST_TOKEN"]
    anilist = Anilist(token)
    print(anilist.get_cover_image(anilist.get_manga_id("another")))
