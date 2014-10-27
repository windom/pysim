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


class Property:
    def __init__(self, short_name, value_producer):
        self.short_name = short_name
        self.value_producer = value_producer

    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        old_value = instance.__dict__.get(self.name, None)

        if not old_value is None:
            instance.propchanged(self, old_value, value)

        instance.__dict__[self.name] = value


class AgentMeta(type):
    def __new__(mcls, name, bases, clsdict):
        props = [(name, val) for name, val in clsdict.items()
                 if isinstance(val, Property)]

        for name, prop in props:
            prop.name = name

        clsprops = []
        for base in bases:
            clsprops.extend(getattr(base, 'properties', []))
        clsprops.extend(prop for _, prop in props)
        clsdict['properties'] = clsprops

        clsobj = super().__new__(mcls, name, bases, clsdict)
        return clsobj


class Agent(metaclass=AgentMeta):
    def __new__(cls):
        new = super().__new__(cls)

        for prop in new.properties:
            setattr(new, prop.name, prop.value_producer())

        return new

    def __init__(self, name=None):
        if name is None:
            self.name = data.random_noun("names")
        else:
            self.name = name

    def reset(self):
        self.messages = []
        self.propchanges = []

    def do_action(self, *request):
        yield
        self.reset()
        pair_agent = yield request
        return pair_agent

    def say(self, message, *args):
        self.messages.append(message.format(*args))

    def propchanged(self, prop, old_value, new_value):
        if prop.short_name:
            self.propchanges.append((prop.short_name, old_value, new_value))

    def roll(self, chance):
        return random.randint(1, 100) <= chance

    def propvalues(self):
        return {prop.short_name: getattr(self, prop.name)
                for prop in self.properties if prop.short_name}

    @action
    def wait(self):
        pass

    def live(self):
        pass

    def __repr__(self):
        return self.name


class TextRenderer:
    def __init__(self, file=sys.stdout, show_debug=False, show_changes=False):
        self.file = file
        self.show_debug = show_debug
        self.show_changes = show_changes

    def render(self, agents):
        for agent in agents:
            if self.show_debug:
                debug_str = utils.pretty_print(agent.propvalues())
            else:
                debug_str = ""

            if self.show_changes:
                def format_change(prop, old_value, new_value):
                    if new_value > old_value:
                        return prop + "+" + str(new_value - old_value)
                    else:
                        return prop + "-" + str(old_value - new_value)
                change_str = " ".join(format_change(*change) for change in agent.propchanges)
                change_str = "[" + change_str + "]"
            else:
                change_str = ""

            head_len = None
            for message in agent.messages:
                if not head_len:
                    head = "{:>15}{}{}  ".format(agent.name.upper(), debug_str, change_str)
                    head_len = len(head)
                    print(head + message, file=self.file)
                else:
                    print(" " * head_len + message, file=self.file)

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

        for agent, live in zip(self.agents, self.lives):
            live.send(responses[agent])

        self.renderer.render(self.agents)
