from copy import deepcopy

class RLInteger:
    # Constructor
    # Initialize from a dictionary {level : realization}
    # Levels are floats ordered in descending order from 1.
    # Realizations are objects of class Integer.
    def __init__(self, map_dict):
        # Error checking
        if not isinstance(map_dict, dict):
            raise TypeError('Input must be a dictionary')
        if 1 not in map_dict:
            raise ValueError('Level 1 must be present in every RL')
        for alpha in map_dict:
            if not 0 < alpha <= 1:
                raise ValueError('Levels must be in (0, 1]')
        self.map_dict = {alpha: deepcopy(obj) for alpha, obj in map_dict.items()}
    
    # Combine level-sets, maintaining order and returning a list
    def combine_levels(self, other):
        # Level-sets
        lvls1,lvls2 = list(self.map_dict.keys()), list(other.map_dict.keys())
        # Iterator indexes, lengths and output list
        i1,i2,levels = 0,0,[]
        # Iterate over level-sets and insert into output maintaining order
        while (i1 < len(lvls1) and i2 < len(lvls2)):
            curr1,curr2 = lvls1[i1],lvls2[i2]
            # Append largest of curr1,curr2
            levels.append(curr1 if curr1 >= curr2 else curr2)
            # Move up the indexes if more or equal (no duplicates)
            i1 = i1+1 if curr1 >= curr2 else i1
            i2 = i2+1 if curr2 >= curr1 else i2
        # Extend with leftover levels
        if i1 != len(lvls1): levels.extend(lvls1[i1:])
        if i2 != len(lvls2): levels.extend(lvls2[i2:])
        return levels

    def __add__(self, other):
        pass
    def __mul__(self,other):
        pass

    # For human readability. 
    # Calls __repr__ internally for keys and values of the dict
    def __str__(self):
        return str(self.map_dict)