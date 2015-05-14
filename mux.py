def mux(l):
    def round(l):
        return [a^b for a,b in zip(l[:-1], l[1:])]
    nl = []
    while l:
        nl.append(l[0])
        l = round(l)
    return nl


def muxxum(l):
    l = mux(l)
    return mux(list(reversed(l)))


def smux(s):
    return ''.join(map(chr, muxxum(list(map(ord, s)))))
