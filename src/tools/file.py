def read(Path):
    try:
        cache = open(Path,mode="r")
        msg = cache.read()
        cache.close()
        return msg
    except:
        return False

def write(Path, sth):
    cache = open(Path, mode="w")
    try:
        cache.write(sth)
        cache.close()
        return True
    except:
        cache.close()
        return False
