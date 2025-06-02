from rlistic.common import validate_mapping, rl_table


class _RLBase:
    """Base class for RL classes, providing shared functionality."""
    _instance_class = None

    def __init__(self, mapping: dict):
        """Initialize the RL with a level-to-object mapping."""
        validate_mapping(mapping)
        if not all(isinstance(obj, type(self)._instance_class) for obj in mapping.values()):
            raise TypeError(f"All mapping values must be instances of {type(self)._instance_class.__name__}")
        self.__mapping = mapping

    @property
    def mapping(self) -> dict:
        """Get the internal RL mapping."""
        return self.__mapping

    def get_level_set(self) -> list[float]:
        """Get the level-set of the RL."""
        return list(self.mapping.keys())

    def get_object(self, level, default=None):
        """Get the object at a given level or a default value."""
        return self.mapping.get(level, default)

    def __combine_levels(self, *args, **kwargs) -> list[float]:
        """Combine levels from this RL and other RLs."""
        def combine_levels_2lists(lvls1, lvls2):
            i1, i2, levels = 0, 0, []
            while i1 < len(lvls1) and i2 < len(lvls2):
                curr1, curr2 = lvls1[i1], lvls2[i2]
                levels.append(curr1 if curr1 >= curr2 else curr2)
                i1 = i1 + 1 if curr1 >= curr2 else i1
                i2 = i2 + 1 if curr2 >= curr1 else i2
            levels.extend(lvls1[i1:] if i1 < len(lvls1) else lvls2[i2:])
            return levels

        levels = self.get_level_set()
        for arg in args:
            other = arg.get_level_set()
            levels = combine_levels_2lists(levels, other)
        for kwarg in kwargs.values():
            other = kwarg.get_level_set()
            levels = combine_levels_2lists(levels, other)
        return levels

    def general_method(self, method_name: str, *args, **kwargs):
        """Apply a method level-wise, checking types via RL_REGISTRY."""
        rl_args = []
        for arg in args:
            if not isinstance(arg, _RLBase):
                arg_type = type(arg)
                try:
                    rl_class = RL_REGISTRY[arg_type]
                except KeyError:
                    raise TypeError(f"No RL class defined for {arg_type.__name__}")
                arg = rl_class({1.0: arg})
            rl_args.append(arg)

        rl_kwargs = {}
        for key, obj in kwargs.items():
            if not isinstance(obj, _RLBase):
                obj_type = type(obj)
                try:
                    rl_class = RL_REGISTRY[obj_type]
                except KeyError:
                    raise TypeError(f"No RL class defined for {obj_type.__name__}")
                obj = rl_class({1.0: obj})
            rl_kwargs[key] = obj

        levels = self.__combine_levels(*rl_args, **rl_kwargs)

        mapping = {}
        curr_self = self.get_object(level=1)
        curr_args = [rl_arg.get_object(level=1) for rl_arg in rl_args]
        curr_kwargs = {key: rl_kwarg.get_object(level=1) for key, rl_kwarg in rl_kwargs.items()}
        prev = None

        for level in levels:
            curr_self = self.get_object(level, curr_self)
            curr_args = [rl_arg.get_object(level, curr) for rl_arg, curr in zip(rl_args, curr_args)]
            curr_kwargs = {
                key: rl_kwarg.get_object(level, curr)
                for (key, rl_kwarg), curr in zip(rl_kwargs.items(), curr_kwargs.values())
            }
            curr = getattr(curr_self, method_name)(*curr_args, **curr_kwargs)
            if level == 1 or curr != prev:
                mapping[level] = curr
            prev = curr

        if len(mapping) == 1:
            return mapping[1]

        result_type = type(mapping[1])
        try:
            rl_class = RL_REGISTRY[result_type]
        except KeyError:
            raise TypeError(f"No RL class defined for {result_type.__name__}")
        return rl_class(mapping)

    def __str__(self) -> str:
        """Get a string representation of the RL as a table."""
        return rl_table(type(self)._instance_class.__name__, self.mapping)

RL_REGISTRY = {}

class A:

    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        return A(self.val + other.val)

    def add(self, other, x=1):
        return A(self.val + other.val + x)

    def __str__(self):
        return str(self.val)
class B:

    def __init__(self, val):
        self.val = val

    def combine(self, other, *args, y=2, **kwargs):
        return B(self.val + other.val + y + sum(args) + sum(kwargs.values))

    def __str__(self):
        return str(self.val)

class RLA(_RLBase):
    _instance_class = A

    def __add__(self, other):
        return self.general_method('__add__', other)

    def add(self, other, x=1):
        return self.general_method('add', other, x)
class RLB(_RLBase):
    _instance_class = B

    def combine(self, other, *args, y=2, **kwargs):
        return self.general_method('combine', other, *args, y=y, **kwargs)

RL_REGISTRY[A] = RLA
RL_REGISTRY[B] = RLB