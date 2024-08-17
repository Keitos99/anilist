import os
from difflib import SequenceMatcher


def get_res_file(res_file: str) -> str:
    data_dir = os.path.join(os.path.dirname(__file__), "res")
    data_path = os.path.join(data_dir, res_file)
    return data_path


def find_matching_media(query: str, medias: dict) -> dict:
    for media in medias:
        titles = list(media["title"].values())
        synonyms = media["synonyms"]

        titles = titles + synonyms
        title = find_matching_title(query, titles)
        if title:
            return media
    return {}


def find_matching_title(query: str, titles: list):
    previous_ratio = 0
    matching_text = ""
    fallback = ""
    for text in titles:
        if not text:
            continue

        ratio = SequenceMatcher(None, text.lower(), query.lower()).ratio()

        if ratio > previous_ratio:
            previous_ratio = ratio
            matching_text = text
        if query.lower() in text.lower():
            fallback = query
    if previous_ratio < 0.8:
        return fallback
    return matching_text
