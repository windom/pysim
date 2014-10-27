import random
import collections
import functools
import sys

import data
import utils


requestItem = collections.namedtuple('requestItem','code needs offers condition')

def shares(request_code, condition=None):
    return requestItem(request_code, True, True, condition)

def needs(request_code, condition=None):
    return requestItem(request_code, True, False, condition)

def offers(request_code, condition=None):
    return requestItem(request_code, False, True, condition)


@utils.optional_arg_decorator
def action(func, *request):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        pair_agent = yield from args[0].do_action(*request)
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
        self.result = []
        for attr_name, attr_short_name, attr_value_producer in self.__attrs__:
            setattr(self, attr_name, attr_value_producer())

    def do_action(self, *request):
        result, self.result = self.result, []
        yield result
        pair_agent = yield request
        return pair_agent

    def debug_info(self):
        return {s: getattr(self,n) for n,s,_ in self.__attrs__ if s}

    def say(self, message, *args):
        message = message.format(*args)
        self.result.append((self, message))

    def roll(self, chance):
        return random.randint(1, 100) <= chance

    @action
    def wait(self):
        pass

    def live(self):
        pass

    def __repr__(self):
        return self.name


class TextRenderer:
    def __init__(self, file=sys.stdout, show_debug=False):
        self.file = file
        self.show_debug = show_debug

    def render(self, results):
        for agent, message in results:
            if self.show_debug:
                debug_str = utils.pretty_print(agent.debug_info())
            else:
                debug_str = ""
            print("{:>15}{}  {}.".format(agent.name.upper(), debug_str, message),
                  file=self.file)

        print(file=self.file)


class World:
    def __init__(self, agents, renderer):
        self.renderer = renderer
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
            return any(needs for _, needs, _, _ in request)

        def request_satisfied(sagent, srequest, dagent, drequest):
            def cond_satisfied(cond, agent):
                return (not cond) or cond(agent)
            def item_satisfied(scode):
                return any(True for dcode, _, doffers, dcond in drequest
                           if doffers and dcode == scode and cond_satisfied(dcond, sagent))
            return all(cond_satisfied(scond, dagent) and item_satisfied(scode)
                       for scode, sneeds, _, scond in srequest if sneeds)

        random.shuffle(requests)

        for agent, request in requests:
            if (not agent in used_agents) and request_needs_anything(request):
                possible_agents = [a for (a, r) in requests if \
                        (a != agent) and \
                        request_satisfied(agent, request, a, r) and \
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

        results = []
        for agent, live in zip(self.agents, self.lives):
            results.extend(live.send(responses[agent]))

        self.renderer.render(results)
