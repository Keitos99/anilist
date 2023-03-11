from difflib import SequenceMatcher
import os
from typing import Dict, List, Tuple


def get_res_file(res_file: str) -> str:
    data_dir = os.path.join(os.path.dirname(__file__), "res")
    data_path = os.path.join(data_dir, res_file)
    return data_path


def get_matching_media(query: str, medias: Dict) -> Dict:
    test = {}
    for media in medias:
        titles = list(media["title"].values())
        synonyms = media["synonyms"]

        titles = titles + synonyms
        title = get_matching_title(query, titles)
        if title:
            return media
    return {}


def get_matching_title(query: str, texts: List):
    previous_ratio = 0
    matching_text = ""
    for text in texts:
        if not text:
            continue

        ratio = SequenceMatcher(None, text.lower(), query.lower()).ratio()

        if ratio > previous_ratio:
            previous_ratio = ratio
            matching_text = text
    if previous_ratio < 0.8:
        return ""
    return matching_text
