from anilist import Anilist

anilist = Anilist()
title = "The Reincarnation Of Countess Diabolique"
print(anilist.get_manga_title(title))
print(anilist.get_manga_id(title))
