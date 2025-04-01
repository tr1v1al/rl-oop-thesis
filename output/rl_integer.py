from copy import deepcopy

class RLInteger:

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

    def combine_levels(self, other):
        lvls1, lvls2 = (list(self.map_dict.keys()), list(other.map_dict.keys()))
        i1, i2, levels = (0, 0, [])
        while i1 < len(lvls1) and i2 < len(lvls2):
            curr1, curr2 = (lvls1[i1], lvls2[i2])
            levels.append(curr1 if curr1 >= curr2 else curr2)
            i1 = i1 + 1 if curr1 >= curr2 else i1
            i2 = i2 + 1 if curr2 >= curr1 else i2
        if i1 != len(lvls1):
            levels.extend(lvls1[i1:])
        if i2 != len(lvls2):
            levels.extend(lvls2[i2:])
        return levels

    def __add__(self, other):
        levels = self.combine_levels(other)
        map_dict, curr1, curr2 = ({}, self.map_dict[1], other.map_dict[1])
        for level in levels:
            curr1 = self.map_dict.get(level, curr1)
            curr2 = other.map_dict.get(level, curr2)
            map_dict[level] = curr1.__add__(curr2)
        return RLInteger(map_dict)

    def __mul__(self, other):
        levels = self.combine_levels(other)
        map_dict, curr1, curr2 = ({}, self.map_dict[1], other.map_dict[1])
        for level in levels:
            curr1 = self.map_dict.get(level, curr1)
            curr2 = other.map_dict.get(level, curr2)
            map_dict[level] = curr1.__mul__(curr2)
        return RLInteger(map_dict)

    def __neg__(self):
        map_dict = {level: obj.__neg__() for level, obj in self.map_dict.items()}
        return RLInteger(map_dict)

    def __str__(self):
        return str(self.map_dict)