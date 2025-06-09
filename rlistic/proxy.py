from functools import partial
from .common import validate_mapping, rl_table
from typing import Callable

# Common special methods to be added to RL class. Can be extended, kept minimal
# for illustration purposes
SPECIAL_METHODS = {
    '__and__', '__or__',    # Logical
    '__neg__', '__pos__', '__abs__',  # Unary
    '__add__', '__sub__', '__mul__', '__truediv__',  # Binary
    '__lt__','__gt__', '__eq__', # Comparison
    '__len__', '__getitem__' # Container
}

class RLMeta(type):
    """ 
    Metaclass for RL class to dynamically add dunder methods to the RL
    class's definition when creating it. 
    """

    @staticmethod
    def make_special_method(method_name: str) -> Callable:
        """
        Factory for producing dunder methods for the RL class. The dunder methods
        delegate to the RL's general_method, same as regular methods.

        Args:
            method_name (str): Name of the special method (e.g., '__add__').

        Returns:
            Callable: Method that calls general_method with the given method_name.
        """

        def special_method(self, *args, **kwargs):
            # Delegate to RL's general_method for RL-behaviour
            return self.general_method(method_name, *args, **kwargs)
        
        return special_method
    
    def __new__(mcs, name, bases, attrs):
        """
        Create the RL class with dunder methods provided in SPECIAL_METHODS.

        Args:
            mcs: The metaclass.
            name (str): Name of the class being constructed.
            bases (tuple): Base classes.
            attrs (dict): Class attributes.

        Returns:
            type: RL class with added dunder methods.
        """
        
        # For each dunder method to be added, create the corresponding dunder 
        # method using the make_special_method factory, then assign that
        # method to the dictionary of attributes of the RL class.
        for method_name in SPECIAL_METHODS:
            attrs[method_name] = RLMeta.make_special_method(method_name)
        return super().__new__(mcs, name, bases, attrs)

class RL(metaclass=RLMeta):
    """
    Proxy class for managing graduality using Representations by Levels (RLs).

    Attributes:
        __instance_class (type): Class of objects affected by graduality.
        __mapping (dict): Dictionary mapping levels (floats in (0,1]) to objects.
    """

    def __init__(self, mapping: dict):
        
        # Validate the level-set and the objects to rlify
        validate_mapping(mapping)
        
        # Save the class of rlified objects and the mapping as private attributes
        self.__instance_class = type(mapping[1])
        self.__mapping = mapping

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
    
    @property
    def instance_class(self) -> type:
        """
        Get the class of objects wrapped in the RL.

        Returns:
            type: Class of the RL's objects.
        """

        return self.__instance_class
    
    @property
    def mapping(self) -> dict:
        """
        Get the internal RL mapping.

        Returns:
            dict: Mapping of levels to objects.
        """
        return self.__mapping

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
        # Positional arguments
        rl_args = [
            RL({1 : arg}) if not isinstance(arg, RL) else arg 
            for arg in args
        ]

        # Keyword arguments
        rl_kwargs = {
            key : (RL({1 : obj}) if not isinstance(obj, RL) else obj)
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
            # If an error occurs, it is caught and the message is prepended
            try:
                curr = getattr(curr_self, method_name)(*curr_args, **curr_kwargs)
            except Exception as e:
                raise type(e)(f"Error in {self.__class__.__name__} at level {level}: {e}") from e

            # Add to mapping only if the object is on level 1
            # or not the same as on the previous level
            if level == 1 or curr != prev: mapping[level] = curr
            prev = curr

        # Return resulting RL, if mapping has 1 level then return the crisp object
        # Otherwise the mapping is empty and None is returned
        return RL(mapping) if len(mapping) > 1 else mapping[1]

    def __getattr__(self, method_name: str) -> Callable:
        """
        Dynamically dispatch undefined method calls to general_method.

        Args:
            method_name (str): Name of the method being accessed.

        Returns:
            Callable: Partial function bound to general_method.
        """

        # Return general_method with bound method name
        return partial(self.general_method, method_name)

    def __str__(self) -> str:
        """
        Get a string representation of the RL as a table.

        Returns:
            str: Table formatted by rl_table showing levels and objects.
        """

        return rl_table(self.instance_class.__name__, self.mapping)

def add_magic_methods(method_names: list[str]) -> None:
    """
    Add magic methods to the RL class dynamically.
    
    Args:
        method_names: List of magic method names (e.g., ['__eq__', '__lt__']).
        
    Raises:
        ValueError: If any method name is invalid (not starting/ending with '__').
        TypeError: If method_names is not a list or contains non-string elements.
    """

    # Error handling
    if not isinstance(method_names, list):
        raise TypeError("method_names must be a list")
    if not all(isinstance(name, str) for name in method_names):
        raise TypeError("All method names must be strings")
    if not all(name.startswith('__') and name.endswith('__') for name in method_names):
        raise ValueError("All method names must be magic methods (start and end with '__')")
    
    # Update SPECIAL_METHODS
    global SPECIAL_METHODS
    SPECIAL_METHODS.update(method_names)
    
    # Add methods to existing RL class using RLMeta's dunder method factory
    for method_name in method_names:
        if method_name not in RL.__dict__:
            setattr(RL, method_name, RLMeta.make_special_method(method_name))