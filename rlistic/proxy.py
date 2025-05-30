from copy import deepcopy
from functools import partial
from .common import validate_mapping, rl_table
from typing import Callable

# Common special methods to be added to RL class
SPECIAL_METHODS = {
    '__and__', '__or__',
    '__neg__', '__pos__', '__abs__',  # Unary
    '__add__', '__sub__', '__mul__', '__truediv__',  # Binary
    '__len__', '__getitem__', '__setitem__', '__delitem__',  # Container
    '__call__', '__enter__', '__exit__',  # Callable/context
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
    
    def __new__(cls, name, bases, attrs):
        """
        Create the RL class with dunder methods provided in SPECIAL_METHODS.

        Args:
            cls: Like self, but the object being instantiated here is a class.
            name (str): Name of the class.
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
        return super().__new__(cls, name, bases, attrs)

class RL(metaclass=RLMeta):
    """
    Proxy class for managing graduality using Representations by Levels (RLs).

    Attributes:
        __instance_class (type): Class of objects affected by graduality.
        __mapping (dict): Dictionary mapping levels (floats in (0,1]) to objects.
    """

    def __init__(self, mapping):
        
        # Validate the level-set and the objects to rlify
        validate_mapping(mapping)
        
        # Save the class of rlified objects and the mapping as private attributes
        self.__instance_class = type(mapping[1])
        self.__mapping = {alpha: deepcopy(obj) for alpha, obj in mapping.items()}

    def get_level_set(self):
        """
        Get the level-set of the RL.

        Returns:
            list[float]: Level-set.
        """
        return list(self.__mapping.keys())
 
    def get_object(self, level, default=None):
        """
        Get the object at a given level or a default value.

        Args:
            level (float): Level to query.
            default: Value to return if level is not found (default: None).

        Returns:
            object: Object at the level or default value.
        """
        return self.__mapping.get(level, default) 
    
    @property
    def instance_class(self):
        """
        Get the class of objects wrapped in the RL.

        Returns:
            type: Class of the RL's objects.
        """

        return self.__instance_class
    
    @property
    def mapping(self):
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
            curr = getattr(curr_self, method_name)(*curr_args, **curr_kwargs)

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


# Run with python -m rlistic.proxy
if __name__ == '__main__':
    class A:
        def __init__(self, val):
            self.val = val
        def __add__(self, other):
            print("called add in A")
            return A(self.val+other.val)
        def __pow__(self, power):
            return A(self.val**power.val)
        def __neg__(self):
            return A(-self.val)
        def bruh(self, o1, o2, o3, o4):
            print("hehe")
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
        
    rla1 = RL({1: A(5), 0.6: A(6)})
    rla2 = RL({1: A(3), 0.6: A(2)})
    rla3 = RL({1: A(100), 0.3: A(55)})
    rla4 = RL({1: A(53), 0.7: A(1), 0.3: A(43), 0.2: A(10), 0.1: A(22)})

    print(dir(RL))
    add_magic_methods(['__pow__'])
    print(rla1**rla2)
    print(dir(RL))

    # Integers
    rla5 = RL({1: 3, 0.6: 2})
    rla6 = RL({1: 7, 0.6: 5})
    print(rla5+rla6)
    # RL-int
    # Level | Object
    # ------+-------
    # 1     | 10
    # 0.6   | 7

    # Lists
    rla7 = RL({1: [0,1], 0.8: [3,4]})
    rla8 = RL({1: [10,50], 0.5: [1,1,1]})
    print(rla7+rla8)
    # RL-list
    # Level | Object
    # ------+------------------
    # 1     | [0, 1, 10, 50]
    # 0.8   | [3, 4, 10, 50]
    # 0.5   | [3, 4, 1, 1, 1]    
    print(rla8.__len__())
    # RL-int
    # Level | Object
    # ------+-------
    # 1     | 2
    # 0.5   | 3

    # Sets
    rla9 = RL({1: {5,3,2}, 0.7: {1,2,7}})
    rla10 = RL({1: {1,6,7}, 0.6: {9,4,10}})
    rl_inter = rla9 & rla10
    rl_union = rla9 | rla10
    print(rl_inter)
    print(rl_union)
    # Level | Object
    # ------+---------
    # 1     | set()
    # 0.7   | {1, 7}
    # 0.6   | set()
    # RL-set
    # Level | Object
    # ------+----------------------
    # 1     | {1, 2, 3, 5, 6, 7}
    # 0.7   | {1, 2, 6, 7}
    # 0.6   | {1, 2, 4, 7, 9, 10}    

    print("Length of the sets:")
    print(len(rla9), len(rla10), sep='\n')
    # Length of the sets:
    # 3
    # 3

    print("Length of the intersection/union")
    print(rl_inter.__len__(), rl_union.__len__(), sep='\n')
    # RL-int
    # Level | Object
    # ------+-------
    # 1     | 0
    # 0.7   | 2
    # 0.6   | 0
    # RL-int
    # Level | Object
    # ------+-------
    # 1     | 6
    # 0.7   | 4
    # 0.6   | 6



    class MySet(set):
        def more_ternary(self, other1, other2):
            return int(len(self & other2) >= len(other1 & other2))
        def around_half_in(self,other):
            ratio = len(self & other)/len(other) # Ratio of intersection/other
            return 1 - 2*abs(ratio-0.5) # Around half relative quantifier (triangular shape)
    rl_myset1 = RL({1:MySet({1,2,3}), 0.8 : MySet({3,4,5})})
    rl_myset2 = RL({1:MySet({1,2,4}), 0.8 : MySet({5,6,7})})
    rl_myset3 = RL({1:MySet({5,6,7}), 0.8 : MySet({5,6,7})})

    print("More A than B in C")
    print(rl_myset1.more_ternary(rl_myset2, rl_myset3))
    print("Around half of A is in B")
    print(rl_myset1.around_half_in(rl_myset2))
    


    # More A than B in C
    # RL-int
    # Level | Object
    # ------+-------
    # 1     | 1
    # 0.8   | 0
    # Around half of A is in B
    # RL-float
    # Level | Object
    # ------+---------------------
    # 1     | 0.6666666666666667
    # 0.8   | 0.6666666666666666

    #print(rla1.bruh(rla2, rla4, o3=rla3, o4=1)

# TODOOOOOOOOOOOOOOOOOOOOO
# ERROR HANDLING
# DOCS
# TYPE HINTING 
# TESTING
# ADD SPECIAL METHODD
# ADD MORE DEFAULT METHODS
# ADD RLINPUT
# must the rl have instances of same class??