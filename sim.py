import random
import collections
import functools

import data
import utils


debug_enabled = True


requestItem = collections.namedtuple('requestItem','code needs offers')

def shares(request_code):
    return requestItem(request_code, True, True)

def needs(request_code):
    return requestItem(request_code, True, False)

def offers(request_code):
    return requestItem(request_code, False, True)


def do_action(*request):
    yield
    pair_agent = yield request
    return pair_agent


@utils.optional_arg_decorator
def action(func, *request):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        pair_agent = yield from do_action(*request)
        if not pair_agent is None:
            kwargs["pair"] = pair_agent
        result = func(*args, **kwargs)
        if result:
            yield from result
    return wrapped


class Agent:
    def __init__(self, name=None):
        if name is None:
            self.name = data.random_noun("names")
        else:
            self.name = name
        for attr_name, attr_short_name, attr_value_producer in self.__attrs__:
            setattr(self, attr_name, attr_value_producer())

    def say(self, message, *args):
        message = message.format(*args)
        if debug_enabled:
            debug_info = utils.pretty_print({s: getattr(self,n) for n,s,_ in self.__attrs__ if s})
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

    def __repr__(self):
        return self.name


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

        def request_needs_anything(request):
            return any(needs for _, needs, _ in request)

        def request_satisfied(srequest, drequest):
            def item_satisfied(scode):
                return any(True for dcode, dneeds, doffers in drequest
                           if doffers and dcode == scode)
            return all(item_satisfied(scode) for scode, sneeds, _ in srequest if sneeds)

        random.shuffle(requests)

        for agent, request in requests:
            if (not agent in used_agents) and request_needs_anything(request):
                possible_agents = [a for (a, r) in requests if \
                        (a != agent) and \
                        request_satisfied(request, r) and \
                        (not a in used_agents)]
                if possible_agents:
                    pair_agent = random.choice(possible_agents)
                    associate(agent, pair_agent)
                    associate(pair_agent, agent)

        return responses

    def day(self):
        requests = []
        for agent, live in zip(self.agents, self.lives):
            request = next(live)
            if request:
                requests.append((agent, request))

        responses = self.produce_responses(requests)
        for agent, live in zip(self.agents, self.lives):
            live.send(responses[agent])

        print()

