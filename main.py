import os

from anilist import Anilist

if __name__ == "__main__":
    TOKEN = os.environ.get("ANILIST_TOKEN", "")
    anilist = Anilist(TOKEN)
    id_jjk = 101517
    search_query = "Nigoru Hitomi de Nani wo Negau: Haiseruku Senki"
    print(anilist.search_manga("i raised the villains preciously"))
