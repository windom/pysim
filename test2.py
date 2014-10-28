
class PropertyDictWrapper:
    def __init__(self, owning_prop, owning_instance, the_dict):
        self.owning_prop = owning_prop
        self.owning_instance = owning_instance
        self.the_dict = the_dict

    def __getitem__(self, key):
        return self.the_dict[key]

class PropertyInstanceWrapper:



class Property:
    def __get__(self, instance, cls):
        value = instance.__dict__[self.name]
        if isinstance(value, dict):
            return PropertyDictWrapper(self, instance, value)
        else:
            return value

    def __set__(self, instance, value):
        old_value = instance.__dict__.get(self.name, None)

        instance.propchanged(self, old_value, value)

        instance.__dict__[self.name] = value

    def value_init(self, instance):
        value = self.value_producer()
        self.__set__(instance, value)


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


class Base(metaclass=PropertyMeta):
    def propchanged(self, prop, old_value, new_value):
        print(self,"Changed",prop.name,"from",old_value,"to",new_value)

class Single(Base):
    val = Property()

    def __init__(self, _val):
        self.val = _val


class Alma(Base):
    x = Property()
    y = Property()


a = Alma()
a.x = 20
a.y = {"egy": Single(50)}

a.y["egy"].val += 100
