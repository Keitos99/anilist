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


def find_matching_title(query: str, titles: list[str]):
    SIMILARITY_THRESHOLD = 0.8

    query_lower = query.lower()
    best_matching_ratio = 0
    best_matching_text = ""
    fallback = ""

    for title in titles:
        if not title:
            continue

        title_lower = title.lower()
        ratio = SequenceMatcher(None, title_lower, query_lower).ratio()

        if ratio > best_matching_ratio:
            best_matching_ratio = ratio
            best_matching_text = title

        if fallback is None and query_lower in title_lower:
            # Use the first title with a matching substring as a fallback
            fallback = title

    if best_matching_ratio >= SIMILARITY_THRESHOLD:
        return best_matching_text

    return fallback
