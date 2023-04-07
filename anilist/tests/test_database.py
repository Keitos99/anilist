from anilist import Anilist
from anilist.database import Database
from anilist.status import AniListType


def test_no_double_saving():
    database = Database()

    database.save(
        "A Breakthrough Brought by Forbidden Master and Disciple",
        "A Breakthrough Brought by Forbidden Master and Disciple",
        124853,
        AniListType.manga,
    )
    counted_rows_after_first_saving = len(database.get_rows())

    database.save(
        "A Breakthrough Brought by Forbidden Master and Disciple",
        "A Breakthrough Brought by Forbidden Master and Disciple",
        124853,
        AniListType.manga,
    )
    counted_rows_after_second_saving = len(database.get_rows())

    assert counted_rows_after_first_saving == counted_rows_after_second_saving

