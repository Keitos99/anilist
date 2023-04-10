from anilist import Anilist
from anilist.status import ReadingStatus

TOKEN = ""
anilist = Anilist(TOKEN)
id_jjk = 101517
search_query = "I’m a Villainess But I Became a Mother"
print(anilist.search_manga(search_query))
