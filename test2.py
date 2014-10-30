import types


def install(target, owning_prop, owning_instance, newprops):
    print("Installing", target)
    if isinstance(target, dict) or isinstance(target, list):
        return PropertyCollectionWrapper(owning_prop, owning_instance, target)
    elif isinstance(target, PropertyBase):
        def _(self, prop, old_value, new_value):
            owning_prop.changed(newprops + prop, owning_instance, old_value, new_value)

        target.__propchange__ = types.MethodType(_, target)
        return target
    else:
        return target


class PropertyCollectionWrapper:
    def __init__(self, owning_prop, owning_instance, wrapped):
        self.owning_prop = owning_prop
        self.owning_instance = owning_instance
        self.wrapped = wrapped

        if isinstance(wrapped, dict):
            for k,v in wrapped.items():
                self.__setitem__(k,v)
        else:
            for i,e in enumerate(wrapped):
                self.__setitem__(i,e)

    def __setitem__(self, key, value):
        old_value = self.wrapped[key]

        #self.owning_prop.changed(["K(" + str(key) + ")"], self.owning_instance, old_value, value)
        self.changed(["K(" + str(key) + ")"], self.owning_instance, old_value, value)

        #value = install(value, self.owning_prop, self.owning_instance, ["K(" + str(key) + ")"])
        value = install(value, self, self.owning_instance, ["K(" + str(key) + ")"])

        self.wrapped[key] = value

    def __getitem__(self, key):
        return self.wrapped[key]

    def changed(self, subprops, instance, old_value, new_value):
        self.owning_prop.changed(subprops, instance, old_value, new_value)


class Property:
    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        old_value = instance.__dict__.get(self.name, None)

        self.changed([], instance, old_value, value)

        value = install(value, self, instance, [self])

        instance.__dict__[self.name] = value

    def value_init(self, instance):
        value = self.value_producer()
        self.__set__(instance, value)

    def changed(self, subprops, instance, old_value, new_value):
        instance.__propchange__([self] + subprops, old_value, new_value)

    def __repr__(self):
        return "P(" + self.name + ")"


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


class PropertyBase(metaclass=PropertyMeta):
    def __propchange__(self, prop, old_value, new_value):
        pass


class Base(PropertyBase):
    def __propchange__(self, prop, old_value, new_value):
        print("[" + type(self).__qualname__ + "]","Changed",prop,"from",old_value,"to",new_value)


class Single(Base):
    val = Property()

    def __init__(self, _val):
        self.val = _val


class Alma(Base):
    x = Property()
    y = Property()

class Korte(Alma):
    pass


a = Alma()
a.x = {"egy": [Alma()]}
a.x["egy"][0].x = "korte"


# a = Alma()
# a.x = 20
# a.y = {"egy": Single(50)}
# a.y["egy"].val += 100

# b = Korte()
# # b.y = [Single(20),Single(30)]
# # b.y[0].val += 10
# # b.y[1].val -= 20

# b.y = Single(30)
# b.y.val += 1000

