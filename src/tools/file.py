def read(Path):
<<<<<<< HEAD
    try:
        cache = open(Path,mode="r")
        msg = cache.read()
        cache.close()
        return msg
    except:
        return False
=======
    cache = open(Path,mode="r")
    msg = cache.read()
    cache.close()
    return msg
>>>>>>> ce248a54161b7d9510a638d77c0edb69b8826f83

def write(Path, sth):
    with open(Path, mode="w") as cache:
        cache.write(sth)
<<<<<<< HEAD
        cache.close()
=======
>>>>>>> ce248a54161b7d9510a638d77c0edb69b8826f83
        return True
