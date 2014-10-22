import random
import collections
import functools

import data

debug_enabled = True

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
		for attr_name, attr_short_name, attr_value in self.__attrs__:
			setattr(self, attr_name, attr_value)

	def say(self, message, *args):
		message = message.format(*args)
		if debug_enabled:
			debug_info = " ".join(s + "=" + str(getattr(self,n)) for n,s,_ in self.__attrs__)
			debug_info = "[{:10}]".format(debug_info)
		else:
			debug_info = ""
		print("{:>15}{}  {}.".format(self.name.upper(), debug_info, message))

	def roll(self, chance):
		return random.randint(1, 100) <= chance

	@action
	def wait(self):
		pass

	def live(self):
		pass


class World:
	def __init__(self, agents):
		self.agents = agents		
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
