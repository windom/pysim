import random

import data
import sim
from sim import action, shares, needs, offers


class Coder(sim.Agent):

    caffeine = sim.Property("caf", lambda: 5)
    codelines = sim.Property("cod", lambda: 0)
    relation = sim.Property("rel", lambda: sim.Dict(int))

    @action(shares("coffe"))
    def drink_coffee(self, pair=None):
        if pair:
            self.say("Kavezok {}", data.withify(pair.name))
            self.together(pair)
        else:
            self.say("Kavezok egyedul")
        self.caffeine += 5

    def write_code(self):
        def coding():
            if self.caffeine >= 8:
                self.codelines += 2
                boosted = True
            else:
                self.codelines += 1
                boosted = False
            return boosted

        if self.roll(10):
            while True:
                pair = yield from self.do_action(needs("codehelp"))
                if pair:
                    boosted = coding()
                    self.say("Elakadtam de segit {}, {}", pair.name,
                             "nagyon kodolunk" if boosted else "kodolunk")
                    break
                else:
                    self.say("Elakadtam es nincs aki segitsen")
        else:
            if self.roll(50):
                pair = yield from self.do_action(offers("codehelp"))
            else:
                pair = yield from self.do_action()
            if pair:
                self.say("Dolgozunk {} problemajan, segitek neki", pair.name)
            else:
                boosted = coding()
                if boosted:
                    self.say("Tele vagyok energiaval, nagyon kodolok")
                else:
                    self.say("Kodolok")

        self.together(pair)

        if self.roll(50):
            self.caffeine -= 1

    def together(self, pair, relation_inc=1):
        if pair:
            self.relation[pair] += relation_inc

    def live(self, world):
        while True:
            if self.caffeine <=3 and self.roll((5-self.caffeine)*20):
                yield from self.drink_coffee()
            else:
                yield from self.write_code()


w = sim.World([Coder() for _ in range(10)],
              sim.TextRenderer(show_debug=True, show_changes=True))

for _ in range(20):
    w.day()
