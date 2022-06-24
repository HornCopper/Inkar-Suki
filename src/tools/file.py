def read(Path):
    cache = open(Path,mode="r")
    msg = cache.read()
    cache.close()
    return msg

def write(Path, sth):
    with open(Path, mode="w") as cache:
        cache.write(sth)
        return True
