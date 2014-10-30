import types


class Tracked:
    def handle_set(self, owning_prop, owning_instance, old_value, value):
        if isinstance(value, Collection):
            value.owning_prop = owning_prop
            value.owning_instance = owning_instance
        elif isinstance(value, Class):
            def __changed__(self, props, old_value, new_value):
                owning_prop.changed(props, owning_instance, old_value, new_value)
            value.__changed__ = types.MethodType(__changed__, value)

        self.changed([], owning_instance, old_value, value)

    def changed(self, subprops, instance, old_value, new_value):
        pass


class Collection(Tracked):
    def __init__(self, base={}):
        self.base = base
        self.owning_prop = None
        self.owning_instance = None

    def __getitem__(self, key):
        return self.base[key]

    def __setitem__(self, key, value):
        try:
            old_value = self.base[key]
        except KeyError:
            old_value = None
        self.handle_set(self, [key], old_value, value)
        self.base[key] = value

    def __delitem__(self, key):
        self.__setitem__(key, None)
        del self.base[key]

    def changed(self, subprops, instance, old_value, new_value):
        self.owning_prop.changed(instance + subprops, self.owning_instance, old_value, new_value)

    def __repr__(self):
        return "{}({!r})".format(type(self).__qualname__, self.base)


class Dict(Collection):
    pass


class List(Collection):
    def append(self, item):
        key = len(self.base)
        self.base.append(None)
        self[key] = item


class Property(Tracked):
    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        old_value = instance.__dict__.get(self.name)
        self.handle_set(self, instance, old_value, value)
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        self.__set__(instance, None)
        del instance.__dict__[self.name]

    def changed(self, subprops, instance, old_value, new_value):
        instance.__changed__([self] + subprops, old_value, new_value)

    def __repr__(self):
        return "{}({})".format(type(self).__qualname__, self.name)


class PropertyMeta(type):
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


class Class(metaclass=PropertyMeta):
    def __changed__(self, props, old_value, new_value):
        pass


def test():
    class Alma(Class):
        x = Property()
        y = Property()

        def __changed__(self, props, old_value, new_value):
            print(self, "Prop", props, "changed", old_value, "-->", new_value)

    a = Alma()
    a.x = Alma()
    a.x.y = Dict({})
    a.x.y["egy"] = Dict({})
    a.x.y["egy"]["ketto"] = Alma()
    a.x.y["egy"]["ketto"].x = Alma()
    a.x.y["egy"]["ketto"].x.y = 20
    a.x.y["egy"]["ketto"].x.y += 1000
