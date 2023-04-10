from anilist import Anilist
from anilist.database import Database
from anilist.status import MediaType


def test_no_double_saving():
    database = Database()

    database.save(
        "A Breakthrough Brought by Forbidden Master and Disciple",
        "A Breakthrough Brought by Forbidden Master and Disciple",
        124853,
        MediaType.MANGA,
    )
    counted_rows_after_first_saving = len(database._get_rows())

    database.save(
        "A Breakthrough Brought by Forbidden Master and Disciple",
        "A Breakthrough Brought by Forbidden Master and Disciple",
        124853,
        MediaType.MANGA,
    )
    counted_rows_after_second_saving = len(database._get_rows())

    assert counted_rows_after_first_saving == counted_rows_after_second_saving

