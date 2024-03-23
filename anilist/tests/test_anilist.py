import os

from anilist import Anilist, find_matching_media, find_matching_title
from anilist.status import ReadingStatus

TOKEN = os.environ.get("ANILIST_TOKEN", "")
anilist = Anilist(TOKEN)


def get_media_from_list(query, lists):  # NOTE: only useful while testing?
    for list in lists:
        entries = list["entries"]
        medias = [entry["media"] for entry in entries]
        media = find_matching_media(query, medias)
        if media:
            return media
    return {}


def test_searching_manga():
    result_title = "The Horizon"
    result_id = 100568

    search_query = "the-horizon"
    assert anilist.get_manga_title(search_query) == result_title
    assert anilist.get_manga_id(search_query) == result_id

    search_query = "the-horizo"
    assert anilist.get_manga_title(search_query) == result_title
    assert anilist.get_manga_id(search_query) == result_id

    search_query = "thehorizo"
    assert anilist.get_manga_title(search_query) == result_title
    assert anilist.get_manga_id(search_query) == result_id

    search_query = "the horizo"
    assert anilist.get_manga_title(search_query) == result_title
    assert anilist.get_manga_id(search_query) == result_id

    search_query = "the horizon"
    assert anilist.get_manga_title(search_query) == result_title
    assert anilist.get_manga_id(search_query) == result_id


def test_reading_status():
    id = 43748  # title: Defense Devil

    media = anilist.get_publishing_status(id)
    publishing_status = media["publishing_status"]
    max_progress = media["progress"]

    assert ReadingStatus.COMPLETED == ReadingStatus.decide_reading_status(
        id, publishing_status, 100, max_progress)
    assert ReadingStatus.COMPLETED == ReadingStatus.decide_reading_status(
        id, publishing_status, 10000, max_progress)
    assert ReadingStatus.CURRENT == ReadingStatus.decide_reading_status(
        id, publishing_status, 10, max_progress)
    assert ReadingStatus.CURRENT == ReadingStatus.decide_reading_status(
        id, publishing_status, 99, max_progress)
    assert ReadingStatus.PLANNING == ReadingStatus.decide_reading_status(
        id, publishing_status, 0, max_progress)
    assert ReadingStatus.PLANNING == ReadingStatus.decide_reading_status(
        id, publishing_status, -20, max_progress)

    id = 85611  # Tokyo Ghoul
    media = anilist.get_publishing_status(id)
    publishing_status = media["publishing_status"]
    max_progress = media["progress"]
    assert ReadingStatus.COMPLETED == ReadingStatus.decide_reading_status(
        id, publishing_status, 181, max_progress)
    assert ReadingStatus.PLANNING == ReadingStatus.decide_reading_status(
        id, publishing_status, 0, max_progress)
    assert ReadingStatus.CURRENT == ReadingStatus.decide_reading_status(
        id, publishing_status, 170, max_progress)


def test_user_infos():
    user_name = "Keitos"
    user_infos = anilist.search_user(user_name)

    assert user_infos["name"] == user_name
    assert user_infos["id"] == 5543995


def test_get_manga_collection():
    user_id = 5543995  # User id of Keitos

    manga_collection = anilist.get_manga_collection_by_id(user_id)

    assert len(manga_collection) > 0


def test_get_matching_text():
    texts = [
        "Übel Blatt 0",
        "07-Ghost",
        "18if",
        "19 Tian",
        "20th Century Boys",
        "86 EIGHTY-SIX Season 2",
        "86 EIGHTY-SIX",
        "86―EIGHTY-SIX",
        "91 Days",
        "A Certain Magical Index II",
        "A Certain Magical Index",
        "A Returner's Magic Should Be Special",
        "A Silent Voice",
        "A, A¹",
        "ABILITY SHOP",
        "ACCA: 13-ku Kansatsu-ka Specials",
        "AHO-GIRL",
        "AJIN: Demi-Human 2",
        "ALDNOAH.ZERO",
        "Absolute Duo",
        "Accel World Ex",
        "Accel World",
        "Accel World: Acchel World.",
        "Aesthetica of a Rogue Hero",
        "After the Rain",
        "Again!!",
        "Ah My Buddha!!",
        "Ai Tenchi Muyo!",
        "Ai Tenchi Muyou!",
        "Ai no Utagoe wo Kikasete",
        "Akame ga KILL!",
        "Akame ga Kill!",
        "Aku no Hana",
        "Akudama Drive",
        "Akumetsu",
        "Aldnoah.Zero Season One",
        "All You Need Is Kill",
        "Amagami SS",
        "And you thought there is never a girl online?",
        "Angel Beats! Heaven's Door",
        "Angel Beats! The Last Operation",
        "Angel Beats!",
        "Angel Beats!: Another Epilogue",
        "Anime Tenchou x Touhou Project",
        "Ano Hi Mita Hana no Namae wo Bokutachi wa Mada Shiranai.",
        "Ano Hi Mita Hana no Namae wo Bokutachi wa Mada Shiranai.: Menma e no Tegami",
        "Anonymous Noise",
        "Another Typical Fantasy Romance",
        "Another",
        "Another: The Other",
        "Anti-Magic Academy: The 35th Test Platoon",
        "Ao Haru Ride",
        "Are You Alice?",
        "Aria the Scarlet Ammo",
        "Arifureta Shokugyou de Sekai Saikyou Prologue",
        "Arifureta: From Commonplace to World’s Strongest",
        "Arslan Senki",
        "As a Reincarnated Aristocrat, I’ll Use My Appraisal Skill to Rise in the World",
        "Assassination Classroom",
        "Athena Complex",
        "Attack on Titan",
        "Ayashimon",
        "B Gata H Kei",
        "BEASTARS",
        "BLAME!",
        "BTOOOM!",
        "BURN THE WITCH",
        "Baka and Test - Summon the Beasts",
        "Baka to Test to Shoukanjuu Spinoffs",
        "Bakemonogatari",
        "Bakuman.",
        "Barbarian Quest",
        "Bastard",
        "Battle Royale",
        "Battle in 5 Seconds",
        "Beautiful Bones -Sakurako's Investigation-",
        "Beelzebub",
        "Beelzebub: Hirotta Akachan wa Daimaou!?",
        "Beelzebub: Kaiketsu!! Beel-bo Meitantei Suiri",
        "Beelzebub: Sakigake!! Beel to Shinsengumi",
        "Ben-To",
        "Berserk",
        "Beyond the Boundary",
        "Billy Bat",
        "Black Bullet",
        "Black Cat",
        "Black Clover",
        "Black Haze",
        "Black Lagoon",
        "Black Torch",
        "Black★Rock Shooter",
        "Bladedance of Elementalers",
        "Blast of Tempest",
        "Bleach",
        "Blood Blockade Battlefront",
        "Blood Lad",
        "Blood on the Tracks",
        "Bloody Monday",
        "Blue Exorcist",
        "Blue Exorcist: The Movie",
        "Blue Flag",
        "Blue Lock",
        "Blue Spring Ride",
        "Bodacious Space Pirates",
        "Boroboro no Elf-san wo Shiawase ni Suru Kusuriuri-san",
        "Boruto: Naruto Next Generations",
        "Brave 10",
        "Brynhildr in the Darkness",
        "Buddy Complex",
        "Bungo Stray Dogs",
        "Buster Keel!",
        "Call of the Night",
        "Damn Reincarnation",
    ]

    assert find_matching_title("20th", texts) == ""
    assert find_matching_title("20th", texts) != "20th Century Boys"
    assert find_matching_title("ubel blatt", texts) == "Übel Blatt 0"
    assert find_matching_title("arsan senki", texts) == "Arslan Senki"
    assert find_matching_title("arsan-senki", texts) == "Arslan Senki"
    assert find_matching_title("-arsan-senki", texts) == "Arslan Senki"
    assert find_matching_title("/damn-reinarnation",
                              texts) == "Damn Reincarnation"


def test_titles_without_strokes():
    # assert anilist.get_manga_id("four knights of the apocalypse") == 129117
    assert (
        anilist.get_manga_id(
            "The Seven Deadly Sins: Four Knights of the Apocalypse")
        == 129117
    )


def test_deep_search_medias():
    manga_collection = anilist.get_manga_collection_by_id(5543995)
    lists = manga_collection["lists"]

    query = "Ariureta Shkugyou deSekai Saikyou"
    media = get_media_from_list(query, lists)
    titles = list(media["title"].values()) + media["synonyms"]
    assert "Arifureta: From Commonplace to World’s Strongest" in titles

    query = "/damn-reinarnation"
    media = get_media_from_list(query, lists)
    titles = list(media["title"].values()) + media["synonyms"]
    assert "Damn Reincarnation" in titles


def test_get_cover_image():
    img_url = anilist.get_cover_image(anilist.get_manga_id("Another"))
    assert (
        img_url
        == "https://s4.anilist.co/file/anilistcdn/media/manga/cover/small/bx54098-NZ21m9i1lZOs.jpg"
    )
