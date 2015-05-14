import random
import itertools
import functools

import utils
from mux import smux as mux


class tok:
    def __init__(self, text):
        self.text = mux(text)

    def gen(self, rules):
        yield self.text

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.text)


class toks:
    def __init__(self, *tokens):
        self.rules = list(map(rule, tokens))

    def __repr__(self):
        return "{}{}".format(type(self).__name__, tuple(self.rules))


class alt(toks):
    def gen(self, rules):
        yield from random.choice(self.rules).gen(rules)

class seq(toks):
    def gen(self, rules):
        yield from itertools.chain.from_iterable(rule.gen(rules)
                                                 for rule in self.rules)


class ref:
    name_prefix = '@'

    def __init__(self, name):
        self.name = mux(name)

    def gen(self, rules):
        yield from rules.gen(self.name)

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.name)


@functools.singledispatch
def rule(token):
    return token

@rule.register(str)
def _(token):
    if token[0] == ref.name_prefix:
        return ref(token[1:])
    else:
        return tok(token)

@rule.register(list)
def _(tokens):
    return alt(*tokens)

@rule.register(tuple)
def _(tokens):
    return seq(*tokens)


class rules(dict):
    def __init__(self, ruledict={}):
        super().__init__({mux(key): rule(value) for key, value in ruledict.items()})

    def __getitem__(self, key):
        return self.postprocess(list(self.gen(key)))

    def __setitem__(self, key, value):
        super().__setitem__(mux(key), rule(value))

    def gen(self, key):
        return super().__getitem__(key).gen(self)

    def postprocess(self, tokens):
        def prepare(toks):
            tok, ntok = toks
            if tok == '$a':
                if ntok[0] in "aeiou":
                    return "az"
                else:
                    return "a"
            else:
                return tok
        return " ".join(map(prepare, zip(tokens, tokens[1:] + ["x"])))

###########################################################################

mux = lambda s: s

hello = rules({
    "nev": ["Gabor", "Jozsi", "Pista"],
    "dolog": ["stajsz", "dolog", "helyzet", "allas"],
    "udvozles": (["Hello", "Szia", "Cso"], "@nev", "mi", "$a", "@dolog"),
    "ketudv": ("@udvozles", "@veg"),
    "veg": "locsics"
    })

print(hello[mux("ketudv")])
print(utils.wrap_lines(repr(hello), 80))
