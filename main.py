import os

from anilist import Anilist
from anilist.status import ReadingStatus

TOKEN = os.environ["ANILIST_TOKEN"]
for env in os.environ:
    print(env)
anilist = Anilist(TOKEN)
id_jjk = 101517
search_query = "I’m a Villainess But I Became a Mother"
print(anilist.search_manga_with_id(117581))
