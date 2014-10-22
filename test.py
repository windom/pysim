import random

import data
import sim


class Coder(sim.Agent):
	
	__attrs__ = [("caffeine", "caf", 5),
	             ("codelines", "cod", 0)]

	def __init__(self, name):
		super().__init__(name)

	@sim.action("kv")
	def drink_coffee(self, pair=None):
		if pair:
			self.say("Kavezok {}", data.withify(pair.name))
		else:
			self.say("Kavezok egyedul")
		self.caffeine += 5

	@sim.action
	def write_code(self):
		if self.caffeine >= 8:
			self.say("Tele vagyok energiaval. Nagyon kodolok")
			self.codelines += 2
		else:
			self.say("Kodolok")
			self.codelines += 1
		if self.roll(50):
			self.caffeine -= 1

	def live(self, world):
		while True:
			if self.caffeine <=3 and self.roll((5-self.caffeine)*20):
				yield from self.drink_coffee()
			else:
				yield from self.write_code()


w = sim.World([Coder(data.random_noun("names")) for _ in range(5)])
for _ in range(100):
	w.day()
