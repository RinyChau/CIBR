import imagehash


def phash(image):
    phash = imagehash.phash(image)
    return [1 if x.item() else 0 for x in phash.hash.flatten()]
