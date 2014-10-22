from functools import singledispatch

@singledispatch
def pretty_print(val):
    return str(val)

@pretty_print.register(dict)
def _(val):
    return "[" + " ".join(pretty_print(k) + "=" + pretty_print(v) for k, v in val.items()) + "]"

