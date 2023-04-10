import csv
import importlib.resources
import os
import shutil
from tempfile import NamedTemporaryFile
from typing import Dict, List

from anilist.status import MediaType
from anilist.tools import get_matching_title, get_res_file


# NOTE: currently a cvs file, but in the future it should use sqlight
class Database:
    TEMP = "/tmp/anilist.csv"

    # columns
    QUERY = "Query"
    ANILIST_TITLE = "Result"
    ANILIST_ID = "ID"
    ANILIST_TYPE = "TYPE"
    FIELDNAMES = [QUERY, ANILIST_TITLE, ANILIST_ID, ANILIST_TYPE]
    # TODO: rename

    def __init__(self, anilist_csv=""):
        if anilist_csv:
            self.ANILIST_CSV = anilist_csv
            return
        self.ANILIST_CSV = "/home/agsayan/.local/share/anilist.csv"

    def update_entry(self, search_query: str, result: str, id: int, typ: MediaType):
        tempfile = NamedTemporaryFile(mode="w", delete=False)
        with open(self.ANILIST_CSV, "r") as csvfile, tempfile:
            reader = csv.DictReader(
                csvfile, delimiter=";", quotechar="|", fieldnames=self.FIELDNAMES
            )
            writer = csv.DictWriter(
                tempfile,
                delimiter=";",
                quotechar="|",
                fieldnames=self.FIELDNAMES,
                escapechar="\n",
            )

            for row in reader:
                if row[self.QUERY] == search_query:
                    print("updating row", row)
                    row[self.QUERY] = search_query
                    row[self.ANILIST_TITLE] = result
                    row[self.ANILIST_ID] = id
                    row[self.ANILIST_TYPE] = typ.name
                row = {
                    self.QUERY: row[self.QUERY],
                    self.ANILIST_TITLE: row[self.ANILIST_TITLE],
                    self.ANILIST_ID: row[self.ANILIST_ID],
                    self.ANILIST_TYPE: row[self.ANILIST_TYPE],
                }

                writer.writerow(row)
        shutil.move(tempfile.name, self.ANILIST_CSV)

    def save_media(self, search_query: str, media: Dict):
        titles = list(media["title"].values()) + media["synonyms"]
        title = get_matching_title(search_query, titles)
        media_type = MediaType(media["type"])
        id = media["id"]
        self.save(search_query, title, id, media_type)

    def save(self, search_query: str, result: str, id: int, typ: MediaType):
        title = self.get_title(search_query=search_query, type=typ)
        database_id = self.get_id(search_query=search_query, type=typ)

        if title and database_id > 0:
            return

        if title and database_id == -1 and id > 0:
            print(
                "Updating entry:\nsearch_query = {}\nresult = {}\ntyp = {}".format(
                    search_query, result, typ.value, typ.value
                )
            )
            self.update_entry(search_query, result, id, typ)
            return

        # skipping, there is already an entry of it
        if title and title == result:
            return

        with open(self.ANILIST_CSV, "a") as f:
            f.write(
                "{};{};{};{}\n".format(search_query, result, id, typ.value)
            )

    def get_title(self, search_query: str, type: MediaType) -> str:
        title = self.read_row(search_query, type, self.ANILIST_TITLE)
        return title

    def get_id(self, search_query: str, type: MediaType, filter_column=QUERY) -> int:
        id = self.read_row(
            search_query, type, self.ANILIST_ID, filter_column=filter_column
        )
        if not id:
            return -1

        if not id.lstrip("-").isnumeric():
            raise Exception(
                f"Found for the search query \"{search_query}\" an non numeric entry: \"{id}\"!")
        return int(id)

    def _get_rows(self) -> List[Dict]:
        with open(self.ANILIST_CSV, "r") as f:
            spamreader = csv.DictReader(
                f, delimiter=";", quotechar="|", fieldnames=self.FIELDNAMES
            )
            cvs_file = [row for row in spamreader]
        return cvs_file

    # FIX: TO SLOW
    def read_row(
        self, search_query: str, typ: MediaType, column: int, filter_column=QUERY
    ) -> str:
        search_query = search_query.lower()
        for row in self._get_rows():
            query = row[filter_column].lower()
            anilist_title = row[self.ANILIST_TITLE].lower()
            anilist_type = MediaType[row[self.ANILIST_TYPE].upper()]

            query = query.lower()
            anilist_title = anilist_title.lower()
            search_query_with_strokes = search_query.replace(" ", "-")
            if (
                query == search_query
                or anilist_title == search_query
                or query == search_query_with_strokes
            ) and anilist_type == typ:
                return row[column]

        return ""
