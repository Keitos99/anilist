import os

from anilist import Anilist

if __name__ == "__main__":
    TOKEN = os.environ.get("ANILIST_TOKEN", "")
    anilist = Anilist(TOKEN)
    print(anilist.get_user())
