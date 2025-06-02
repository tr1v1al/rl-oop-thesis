from copy import deepcopy
from .common import validate_mapping, rl_table

# Registry for RL classes. All created RL classes have an entry here.
# Unless explicitly rlified by the user, an RL class is not injected
# into the global namespace. So if it is created as a by-product of 
# an operation, it is stored here. key = Class, value = RLClass.
RL_REGISTRY = {}

# Methods to ignore during rlification
ignore_methods = [
    '__init__', '__str__', '__repr__', '__getattr__', '__setattr__',
    '__new__', '__class__', '__getattribute__', '__delattr__'
]

class _RLBase:
    """ Base class for RL classes, providing shared functionality. """
    
    # Class atribute that determines to which class A the RLA corresponds
    _instance_class = None   

    def __init__(self, mapping: dict):
        """Initialize the RL with a level-to-object mapping."""

        # Validate the level-set and the objects to rlify
        validate_mapping(mapping)
        
        # Ensure that the RLA class can only be instantiated with objects of A
        if not all(isinstance(obj, type(self)._instance_class) for obj in mapping.values()):
            raise TypeError(f"All mapping values must be instances of {type(self)._instance_class.__name__}")
        
        # Save the mapping of levels to objects
        self.__mapping = {alpha: deepcopy(obj) for alpha, obj in mapping.items()}

    @property
    def mapping(self) -> dict:
        """
        Get the internal RL mapping.

        Returns:
            dict: Mapping of levels to objects.
        """

        return self.__mapping

    def get_level_set(self) -> list[float]:
        """
        Get the level-set of the RL.

        Returns:
            list[float]: Level-set.
        """

        return list(self.mapping.keys())
 
    def get_object(self, level, default=None):
        """
        Get the object at a given level or a default value.

        Args:
            level (float): Level to query.
            default: Value to return if level is not found (default: None).

        Returns:
            object: Object at the level or default value.
        """

        return self.mapping.get(level, default) 

    def __combine_levels(self, *args, **kwargs) -> list[float]:
        """
        Combine levels from this RL and other RLs provided as arguments.

        Args:
            *args: RLs passed as positional arguments.
            **kwargs: RLs passed as keyword arguments.

        Returns:
            list[float]: Combined levels in descending order.
        """

        # Helper function for merging two ordered arrays (descending)
        def combine_levels_2lists(lvls1, lvls2):
            i1, i2, levels = 0, 0, []
            # Merge until reaching the end of an array
            while i1 < len(lvls1) and i2 < len(lvls2):
                curr1, curr2 = lvls1[i1], lvls2[i2]
                levels.append(curr1 if curr1 >= curr2 else curr2)
                i1 = i1 + 1 if curr1 >= curr2 else i1
                i2 = i2 + 1 if curr2 >= curr1 else i2
            # Extend with remaining levels
            if i1 != len(lvls1): levels.extend(lvls1[i1:])
            if i2 != len(lvls2): levels.extend(lvls2[i2:])
            return levels   

        # Levels of self
        levels = self.get_level_set()
        
        # Combine with levels from other RLs
        # Positional RL arguments
        for arg in args:
            other = arg.get_level_set()
            levels = combine_levels_2lists(levels, other)
        
        # Keyword RL arguments
        for kwarg in kwargs.values():
            other = kwarg.get_level_set()
            levels = combine_levels_2lists(levels, other)

        return levels

    def general_method(self, method_name: str, *args, **kwargs):
        """
        Apply a method level-wise across RLs, aggregating the result in an RL.
        Arguments can be RLs or crisp, the latter are extended to other levels.
        The output is an RL or crisp, if the objects on all levels are equal.

        Args:
            method_name (str): Name of the method to apply (e.g., '__add__', 'union').
            *args: Positional arguments, may include RLs or crisp objects.
            **kwargs: Keyword arguments, may include RLs or crisp objects.

        Returns:
            RL or object: Resulting RL or crisp object (if same object on all levels).
        """
         
        # RLify crisp arguments with list/dict comprehension
        # If an argument is not a child of the base RL class, it is treated as crisp,
        # and rlified. If the object has a corresponding RL class, its RL is instantiated
        # If not, the RL class is created and added to the registry, and then
        # the RL is instantiated.

        # Positional arguments
        rl_args = [
            RL_REGISTRY.setdefault(type(arg), rlify(type(arg)))({1.0: arg}) 
            if not isinstance(arg, _RLBase) else arg
            for arg in args
        ]

        # Keyword arguments
        rl_kwargs = {
            key: RL_REGISTRY.setdefault(type(obj), rlify(type(obj)))({1.0: obj}) 
            if not isinstance(obj, _RLBase) else obj
            for key, obj in kwargs.items()
        }

        # Get all levels
        levels = self.__combine_levels(*rl_args, **rl_kwargs)

        # Mapping dictionary for the returned RL
        mapping = {}

        # Objects at current level, used to extend to levels not present in the level set
        # Initialized to level 1. Self, positional and keyword arguments.
        curr_self = self.get_object(level=1)
        curr_args = [rl_arg.get_object(level=1) for rl_arg in rl_args]
        curr_kwargs = {key : rl_kwarg.get_object(level=1) for key, rl_kwarg in rl_kwargs.items()}

        # Perform operations levelwise
        prev = None
        for level in levels:
            # Retrieve objects at the current level. 
            # If level is not present, fall back to previous level
            curr_self = self.get_object(level, curr_self)
            curr_args = [rl_arg.get_object(level, curr) for rl_arg, curr in zip(rl_args, curr_args)]
            curr_kwargs = {
                key : rl_kwarg.get_object(level, curr) 
                for (key, rl_kwarg), curr 
                in zip(rl_kwargs.items(), curr_kwargs.values())
            }
            # Operate with arguments at the current level. Retrieve the method_name method
            # for self and then call it with positional and keyword arguments
            curr = getattr(curr_self, method_name)(*curr_args, **curr_kwargs)

            # Add to mapping only if the object is on level 1
            # or not the same as on the previous level
            if level == 1 or curr != prev: mapping[level] = curr
            prev = curr

        # Return crisp object if RL only has one level
        if len(mapping) == 1:
            return mapping[1]
        
        # Get the class of the objects obtained as output 
        result_type = type(mapping[1])
        
        # If the output is of a class yet to be rlified, rlify it and
        # add the appropriate entry in the RL registry.
        if result_type not in RL_REGISTRY:
            RL_REGISTRY[result_type] = rlify(result_type)
        
        # Return an RL of the corresponding class
        return RL_REGISTRY[result_type](mapping)
    
    def __str__(self) -> str:
        """
        Get a string representation of the RL as a table.

        Returns:
            str: Table formatted by rl_table showing levels and objects.
        """

        return rl_table(type(self)._instance_class.__name__, self.mapping)


def rlify(original_class: type) -> type:
    """
    Funcittion that rlifies a given class.
    
    Args:
        original_class (type): Class to be rlified.

    Returns:
        type: Corresponding RL class.
    """

    # Check if input is a class
    if not isinstance(original_class, type):
        raise TypeError("original_class must be a class")

    # If the class has already been rlified, return the entry from the registry
    if original_class in RL_REGISTRY:
        return RL_REGISTRY[original_class]

    # Get the class's name
    class_name = original_class.__name__

    # Method factory for the RL class
    # Returns a method that delegates to general_method with given method_name
    def make_method(method_name):
        def method(self, *args, **kwargs):
            return self.general_method(method_name, *args, **kwargs)
        return method

    # Dictionary of the attributes of the RL class
    # Class attribute _instance_class is set to the original_class
    # being rlified, binding the produced RL class to it.
    attrs = {'_instance_class': original_class}

    # Add all the original class's methods to the RL class. Iterate over attributes.
    for method_name in dir(original_class):
        # Ignore unwanted magic methods
        if method_name in ignore_methods:
            continue
        # Get the attribute, if it is callable, add it with the method factory
        method = getattr(original_class, method_name)
        if not callable(method):
            continue
        attrs[method_name] = make_method(method_name)

    # Dynamically create the RL class with type. The RL class will have the name
    # RLoriginalclassname, it will inherit from _RLBase, and have the attributes
    # we copied from the original class
    RLClass = type(f"RL{class_name}", (_RLBase,), attrs)
    
    # Add newly created RL class to the RL registry
    RL_REGISTRY[original_class] = RLClass

    # Return it
    return RLClass


# TESTEO

class A:
    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        return A(self.val + other.val)

    def __mul__(self, other):
        return A(self.val*other)

    def __sub__(self, other):
        return self.val - other.val
    def mymethod(self, other=66):
        return A(self.val + 10 + other)
    def __str__(self):
        return str(self.val)

RLA = rlify(A)

rla1 = RLA({1: A(10), 0.8: A(3)})
rla2 = RLA({1: A(5), 0.7: A(66)})
print(RL_REGISTRY)
print(rla1+rla2)
print(rla1*10)
print(rla1 - rla2)
RLint = rlify(int)
print(RL_REGISTRY)
rlint1 = RLint({1:10, 0.8: 5})
rlint2 = RLint({1:5, 0.7: 3})
print(rlint1*rlint2)
print(dir())
# rla3 = RLA({1: 1, 0.8 : 5})

print(rla1.mymethod())
