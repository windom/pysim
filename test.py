import random
import collections
import functools

import data

def optional_arg_decorator(fn):
	def wrapped_decorator(*args, **kwargs):
		if len(args) == 1 and callable(args[0]):
			return fn(args[0])
		else:
			def real_decorator(decoratee):
				return fn(decoratee, *args, **kwargs)
			return real_decorator
	return wrapped_decorator


@optional_arg_decorator
def action(func, request=None):
	@functools.wraps(func)
	def wrapped(*args, **kwargs):
		yield
		pair_agent = yield request
		if not pair_agent is None:
			kwargs["pair"] = pair_agent
		result = func(*args, **kwargs)
		if result:
			yield from result
	return wrapped


class Agent:
	def __init__(self, name):
		self.name = name

	def say(self, message):
		print("{:>15}  {}.".format(self.name.upper(), message))

	@action
	def wait(self):
		pass

	@action("barat")
	def baratkozas(self, pair=None):
		if pair:
			self.say("Baratkozok " + data.withify(pair.name))
		else:
			self.say("Baratkoztam volna, de nem volt kivel")

	@action("dugas")
	def dugas(self, pair=None):
		if pair:
			self.say("Dugok " + data.withify(pair.name))
		else:
			self.say("Dugtam volna, de nem volt kivel")

	@action
	def uldogeles(self):
		self.say("Uldogelek")
		yield from self.alldogalas()

	@action("all")
	def alldogalas(self, pair=None):
		if pair:
			self.say("Alldogalok " + data.withify(pair.name))
		else:
			self.say("Alldogalok egyedul")

	def live(self, world):
		while True:
			d = random.randint(1,100)
			if d <= 40:
				yield from self.baratkozas()
			elif d <= 40 + 40:
				yield from self.dugas()
			else:
				yield from self.uldogeles()

	def __repr__(self):
		return "Agent_" + self.name


class World:
	def __init__(self):
		self.agents = [Agent(data.random_noun("names")) for _ in range(5)]
		
		self.lives = [agent.live(self) for agent in self.agents]
		for live in self.lives:
			next(live)

	def produce_responses(self, requests):
		used_agents = set()
		responses = collections.defaultdict(lambda: None)

		def associate(agent, pair_agent):
			responses[agent] = pair_agent
			used_agents.add(pair_agent)

		for agent, request in requests:
			if not agent in used_agents:
				possible_agents = [a for (a, r) in requests if (a != agent) and (r == request) and (not a in used_agents)]
				if possible_agents:
					pair_agent = random.choice(possible_agents)
					associate(agent, pair_agent)
					associate(pair_agent, agent)

		return responses

	def day(self):
		requests = []
		for agent, live in zip(self.agents, self.lives):
			request = next(live)
			if not request is None:
				requests.append((agent, request))

		responses = self.produce_responses(requests)
		for agent, live in zip(self.agents, self.lives):
			live.send(responses[agent])

		print()


w = World()
for _ in range(20):
	w.day()
