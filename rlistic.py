from copy import deepcopy

# Methods to ignore in the original class for rlification
ignore_methods = ['__init__', '__str__', '__repr__', '__getattr__', '__setattr__']

# RLification function that takes the class to be rlified as input
def rlify(original_class):
    class_name = original_class.__name__    # Extract class name
    
    # Create our RL class
    class RLClass:
        # Initialization
        def __init__(self, map_dict):
            if not isinstance(map_dict, dict):
                raise TypeError('Input must be a dictionary')
            if 1 not in map_dict:
                raise ValueError('Level 1 must be present in every RL')
            prev = 1
            for alpha in map_dict:
                if prev < alpha:
                    raise ValueError('Levels must be in descending order')
                prev = alpha
                if not 0 < alpha <= 1:
                    raise ValueError('Levels must be in (0, 1]')
            self.map_dict = {alpha: deepcopy(obj) for alpha, obj in map_dict.items()}

        # Combination of the levels of this RL and the one passed as a parameter
        def combine_levels(self, other):
            lvls1, lvls2 = list(self.map_dict.keys()), list(other.map_dict.keys())
            i1, i2, levels = 0, 0, []
            while i1 < len(lvls1) and i2 < len(lvls2):
                curr1, curr2 = lvls1[i1], lvls2[i2]
                levels.append(curr1 if curr1 >= curr2 else curr2)
                i1 = i1 + 1 if curr1 >= curr2 else i1
                i2 = i2 + 1 if curr2 >= curr1 else i2
            if i1 != len(lvls1): levels.extend(lvls1[i1:])
            if i2 != len(lvls2): levels.extend(lvls2[i2:])
            return levels
        
        # String representation
        def __str__(self):
            return str(self.map_dict)

    # Factory function for creating unary methods
    def make_unary_method(method_name):
        def unary_method(self):
            map_dict = {level: getattr(obj, method_name)() for level, obj in self.map_dict.items()}
            return RLClass(map_dict)
        return unary_method
    
    # Factory function for creating binary methods
    def make_binary_method(method_name):
        def binary_method(self, other):
            if not hasattr(other, 'map_dict'):
                other = RLClass({level: deepcopy(other) for level in self.map_dict})
            levels = self.combine_levels(other)
            map_dict, curr1, curr2 = {}, self.map_dict[1], other.map_dict[1]
            for level in levels:
                curr1 = self.map_dict.get(level, curr1)
                curr2 = other.map_dict.get(level, curr2)
                map_dict[level] = getattr(curr1, method_name)(curr2)
            return RLClass(map_dict)
        return binary_method

    # Iterate over the methods of the original class and dynamically create
    # corresponding methods for the RL class using the factory functions above
    for method_name in dir(original_class):
        if method_name in ignore_methods:   # Continue if methods is to be ignored
            continue
        method = getattr(original_class, method_name)   # Get the method
        # Check is attribute is callable (method) and is user defined
        if not hasattr(method, '__call__') or not hasattr(method, '__code__'):
            continue
        arg_count = method.__code__.co_argcount     # Get the number of arguments
        # Add the method to the RL class
        if arg_count == 1:  # Unary (self)
            setattr(RLClass, method_name, make_unary_method(method_name))
        elif arg_count == 2:  # Binary (self, other)
            setattr(RLClass, method_name, make_binary_method(method_name))
    # Assign name to the RL class, acts as a label
    RLClass.__name__ = f"RL{class_name}"
    return RLClass