def hprint(s: str):
    print(f"\x1b[0;31;49m{s}\x1b[0m") # ANSI Code ending on 49m has "transparent" background
