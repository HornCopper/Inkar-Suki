def read(Path):
    try:
        cache = open(Path,mode="r")
        return cache.read()
    except:
        return False

def write(Path, sth):
    with open(Path, mode="w") as cache:
        cache.write(sth)
        return True