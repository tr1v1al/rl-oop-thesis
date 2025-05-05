from copy import deepcopy
from functools import partial

# Common special methods to be added to RL class
SPECIAL_METHODS = [
    '__neg__', '__pos__', '__abs__',  # Unary
    '__add__', '__sub__', '__mul__', '__truediv__',  # Binary
    '__len__', '__getitem__', '__setitem__', '__delitem__',  # Container
    '__call__', '__enter__', '__exit__',  # Callable/context
]

# Metaclass for our RL class
class RLMeta(type):
    # Special method factory
    @staticmethod
    def make_special_method(method_name):
        def special_method(self, *args, **kwargs):
            # Use general_method from RL class
            return self.general_method(method_name, *args, **kwargs)
        return special_method
    
    # Add special methods to the class when creating it
    def __new__(cls, name, bases, attrs):
        for method_name in SPECIAL_METHODS:
            attrs[method_name] = RLMeta.make_special_method(method_name)
        return super().__new__(cls, name, bases, attrs)

class RL(metaclass=RLMeta):
    # Initialization
    def __init__(self, mapping):
        # Error checking
        if not isinstance(mapping, dict):
            raise TypeError('Input must be a dictionary')
        if 1 not in mapping:
            raise ValueError('Level 1 must be present in every RL')
        
        prev = 1
        for alpha in mapping:
            if prev < alpha:
                raise ValueError('Levels must be in descending order')
            prev = alpha
            if not 0 < alpha <= 1:
                raise ValueError('Levels must be in (0, 1]')
        
        instance_classes = {type(obj) for obj in mapping.values()}
        if len(instance_classes) != 1: 
            raise TypeError('All instances must be of the same class')
        
        # Save class of instances and levels as private attributes
        self.__instance_class = instance_classes.pop()
        self.__mapping = {alpha: deepcopy(obj) for alpha, obj in mapping.items()}

    # Return the level set of the RL
    def level_set(self):
        return list(self.__mapping.keys())
    
    # Return object at a given level or the provided default value
    def get_object(self, level, default=None):
        return self.__mapping.get(level, default) 

    # Combine levels of this RL and other RLs passed as parameters
    def __combine_levels(self, *args, **kwargs):
        # Merging of two ordered arrays (descending order)
        def combine_levels_2lists(lvls1, lvls2):
            i1, i2, levels = 0, 0, []
            while i1 < len(lvls1) and i2 < len(lvls2):
                curr1, curr2 = lvls1[i1], lvls2[i2]
                levels.append(curr1 if curr1 >= curr2 else curr2)
                i1 = i1 + 1 if curr1 >= curr2 else i1
                i2 = i2 + 1 if curr2 >= curr1 else i2
            # Extend remaining
            if i1 != len(lvls1): levels.extend(lvls1[i1:])
            if i2 != len(lvls2): levels.extend(lvls2[i2:])
            return levels        
        
        # Levels of self
        levels = self.level_set()

        # Combine with levels from other RLs, positional and keyword
        for arg in args:
            other = arg.level_set()
            levels = combine_levels_2lists(levels, other)
        
        for kwarg in kwargs.values():
            other = kwarg.level_set()
            levels = combine_levels_2lists(levels, other)

        return levels
    
    # Wrapper with RL logic for methods
    def general_method(self, method_name, *args, **kwargs):
        # RLify crisp positional and keyword arguments with list/dict comprehension
        rl_args = [
            RL({1 : arg}) if not isinstance(arg, RL) else arg 
            for arg in args
        ]

        rl_kwargs = {
            level : (RL({1 : obj}) if not isinstance(obj, RL) else obj)
            for level, obj in kwargs.items()
        }

        # Get all levels
        levels = self.__combine_levels(*rl_args, **rl_kwargs)

        # Mapping dictionary for the returned RL
        mapping = {}
        curr_self = self.get_object(level=1)
        curr_args = [rl_arg.get_object(level=1) for rl_arg in rl_args]
        curr_kwargs = {key : rl_kwarg.get_object(level=1) for key, rl_kwarg in rl_kwargs.items()}
        
        # Perform operations levelwise
        for level in levels:
            curr_self = self.get_object(level, curr_self)
            curr_args = [rl_arg.get_object(level, curr) for rl_arg, curr in zip(rl_args, curr_args)]
            curr_kwargs = {
                key : rl_kwarg.get_object(level, curr) 
                for (key, rl_kwarg), curr 
                in zip(rl_kwargs.items(), curr_kwargs)}
            mapping[level] = getattr(curr_self, method_name)(*curr_args, **curr_kwargs)
        
        # Return resulting RL
        return RL(mapping)

    # Dynamic method dispatch. 
    # Intercept method calls when they are not defined in the class
    def __getattr__(self, method_name):
        # SKIP PROBLEMATIC DUNDERS. EXPLICIT LOOKUP IS CAUGHT BY GETATTR UNLIKE IMPLICIT
        # Return wrapper with bound method name
        return partial(self.general_method, method_name)

    # String representation of an RL
    def __str__(self):
        return str(self.__mapping)
    
class A:
    def __init__(self, val):
        self.val = val
    def __add__(self, other):
        print("called add in A")
        return A(self.val+other.val)
    def __neg__(self):
        return A(-self.val)
    def bruh(self, o1, o2, o3, o4):
        return "bruh"
    # def genmethod(self, methodname, arg):
    #     result = getattr(self.val, methodname)(arg.val)
    #     return A(result)    
    # def __getattr__(self, methodname):
    #     print("he")
    #     return partial(self.genmethod, methodname)
    def lmao(self):
        return "lmao"
    def __repr__(self):
        return str(self.val)
    
rla1 = RL({1: A(5), 0.8: A(5)})
rla2 = RL({1: A(3), 0.6: A(2)})
rla3 = RL({1: A(100), 0.3: A(55)})
rla4 = RL({1: A(53), 0.7: A(1), 0.3: A(43), 0.2: A(10), 0.1: A(22)})
print(rla1.bruh(rla2, rla4, o3=rla3, o4=1))
print(rla1+rla2)
