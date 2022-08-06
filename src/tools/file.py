def read(Path):
    try:
        cache = open(Path,mode="r", encoding="utf-8")
        msg = cache.read()
        cache.close()
        return msg
    except:
        return False

def write(Path, sth):
    cache = open(Path, mode="w", encoding="utf-8")
    try:
        cache.write(sth)
        cache.close()
        return True
    except:
        cache.close()
        return False
