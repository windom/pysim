from functools import singledispatch


@singledispatch
def pretty_print(val):
    return str(val)


@pretty_print.register(dict)
def _(val):
    return "[" + " ".join(pretty_print(k) + "=" + pretty_print(v) for k, v in val.items()) + "]"


def optional_arg_decorator(fn):
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, *args, **kwargs)
            return real_decorator
    return wrapped_decorator
