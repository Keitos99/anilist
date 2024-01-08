import os

from anilist import Anilist
from anilist.status import ReadingStatus

# TOKEN = os.environ["ANILIST_TOKEN"]
anilist = Anilist()
id_jjk = 101517
search_query = "Nigoru Hitomi de Nani wo Negau: Haiseruku Senki"
print(anilist.search_manga("i raised the villains preciously"))
