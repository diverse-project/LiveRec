def genRandom(ia = 3877, ic = 29573, im = 139968):
    seed = 42
    imf = float(im)
    while 1:
        seed = (seed * ia + ic) % im
        return seed / imf

genRandom()

