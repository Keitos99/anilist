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
from anilist.status import MediaType, PublishingStatus, ReadingStatus
from anilist.tools import get_matching_media, get_matching_title


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
        raise Exception(
            f"Unexpected status code returned: {response.status_code}")


class Anilist:
    URI = "https://graphql.anilist.co"
    CONTENT_TYP = "application/json"
    ACCEPT = "application/json"
    DO_NOT_UPDATE = -2

    # based on https://anilist.github.io/ApiV2-GraphQL-Docs/
    def __init__(self, authorization: str = None, database=Database()):
        self.database = database

        if not authorization:
            self.header = None
            return

        self.header = {
            "Authorization": authorization,
            "Content-Type": self.CONTENT_TYP,
            "Accept": self.ACCEPT,
        }

    def get_publishing_status(self, media_id: int):
        query = graphql.MAX_PROGRESS_QUERY
        variables = {"id": media_id, "page": 1, "perPage": 100}
        response = _run_query(self.URI, query=query, variables=variables)
        medias = response["data"]["Page"]["media"]

        if len(medias) == 0:
            raise Exception(
                f"Could not retrieve the reading status for the id: {media_id}!\n" +
                "Check if this the correct is the correct id!")

        media = medias[0]
        publishing_status = PublishingStatus(media["status"])
        max_progress = (
            media["chapters"] if media["chapters"] != None else media["episodes"]
        )
        media = {}
        media["progress"] = max_progress
        media["publishing_status"] = publishing_status

        return media

    def update_progress(self, media_id: int, progress: int, reading_status: ReadingStatus = None) -> bool:
        if not reading_status:
            media = self.get_publishing_status(media_id)
            max_progress = media["progress"]
            publishing_status = media["publishing_status"]
            reading_status = ReadingStatus.decide_reading_status(
                media_id, publishing_status, progress, max_progress)

        if not self.header:
            raise Exception(
                "You must add your anilist token to update entries")

        if media_id < 0:
            raise Exception("id={} must be positive".format(media_id))

        if progress < 0:
            raise Exception("progress={} must be positive".format(progress))

        try:
            query = graphql.MEDIA_PROGRESS_MUTATION
            variables = {
                "mediaId": media_id,
                "status": reading_status.value,
                "progress": progress,
            }
            response = _run_query(
                self.URI, query=query, headers=self.header, variables=variables
            )
            saveMediaListEntry = response["data"]["SaveMediaListEntry"]
            if media_id == saveMediaListEntry["mediaId"] and progress == saveMediaListEntry["progress"]:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def _search(self, type: MediaType, search_query: str) -> Dict:
        search_query = search_query.replace("\n", "")
        title = None
        id = -1

        id = self.database.get_id(search_query, type)
        if id > 0:  # was once searched, so choosing the correct one can be skipped
            response = _run_query(
                self.URI,
                query=graphql.SEARCH_QUERY,
                variables={"id": id, "typ": type.value},
            )
            page = response["data"]["Page"]
            total = page["pageInfo"]["total"]
            medias = page["media"]
            return get_matching_media(search_query, medias)

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
        return self._search(MediaType.MANGA, search_query)

    def search_anime(self, search_query: str) -> Dict:
        return self._search(MediaType.ANIME, search_query)

    def get_manga_title(self, search_query: str) -> int:
        if self.database.get_id(search_query, MediaType.MANGA) == self.DO_NOT_UPDATE:
            return self.database.get_title(search_query, MediaType.MANGA)

        title = self.database.get_title(search_query, MediaType.MANGA)
        if title:
            return title

        manga = self.search_manga(search_query=search_query)
        if not manga:
            self.database.save(
                search_query, search_query, -1, MediaType.MANGA)
            return ""

        self.database.save_media(search_query, manga)
        titles = list(manga["title"].values()) + manga["synonyms"]
        return get_matching_title(search_query, titles)

    def get_manga_id(self, search_query: str) -> int:
        id = self.database.get_id(search_query, MediaType.MANGA)
        if id == self.DO_NOT_UPDATE:
            return id

        if id > 0:
            return id

        manga = self.search_manga(search_query=search_query)
        if not manga:
            return -1

        self.database.save_media(search_query, manga)
        return manga["id"]

    def get_cover_image(self, media_id: int) -> str:
        variables = {"id": media_id, "page": 1, "perPage": 1,
                     "type": MediaType.MANGA.value}
        try:
            return _run_query(
                uri=self.URI,
                query=graphql.SEARCH_IMAGES_QUERY,
                variables=variables,
            )["data"]["Page"]["media"][0]["coverImage"]["medium"]
        except Exception as e:
            raise Exception(
                f"Could not find a image for the id \"{media_id}\". Is it correct?")

    def search_user(self, user_name: str):
        variables = {"search": user_name, "sort": "USERNAME"}
        result = _run_query(
            uri=self.URI, query=graphql.SEARCH_USER_QUERY, variables=variables
        )

        users = result["data"]["Page"]["users"]
        for user in users:
            if user["name"] == user_name:
                return user
        return None

    def get_manga_collection_by_name(self, user_name: str) -> Dict:
        user = self.search_user(user_name)
        if not user:
            return {}

        user_id = user["id"]
        return self.get_manga_collection_by_id(user_id)

    def get_manga_collection_by_id(self, user_id: int) -> Dict:
        variables = {"userId": user_id}
        result = _run_query(
            uri=self.URI, query=graphql.MANGA_LIST_COLLECTION_QUERY, variables=variables
        )
        lists = result["data"]["MediaListCollection"]["lists"]

        mangas = {}
        for list in lists:
            entries = list["entries"]
            for entry in entries:
                reading_status = ReadingStatus[entry["status"]]
                media = entry["media"]
                id = media["id"]
                title = media["title"]
                media_status = PublishingStatus(media["status"])
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


if __name__ == "__main__":
    token = os.environ["ANILIST_TOKEN"]
    anilist = Anilist(token)
    print(anilist.get_cover_image(anilist.get_manga_id("another")))
