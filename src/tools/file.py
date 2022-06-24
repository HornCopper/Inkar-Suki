def read(Path):
    try:
        cache = open(Path,mode="r")
        msg = cache.read()
        cache.close()
        return msg
    except:
        return False

def write(Path, sth):
    with open(Path, mode="w") as cache:
        cache.write(sth)
        cache.close()
        return True
