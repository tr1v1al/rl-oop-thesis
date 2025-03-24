from input.integer import Integer
#from expected.rl_integer_expected import RLInteger
from output.rl_integer import RLInteger

int1,int2,int3,int4 = Integer(5),Integer(66),Integer(10), Integer(-17)
RL1 = RLInteger({1:int1, 0.8:int2, 0.4:int3})
RL2 = RLInteger({1:int4, 0.95:int1, 0.2:int3, 0.1:int1})

print(int1+int2)
print(int1*int2)
print(-int1)
print(type(int1+int2))
print(RL1)
print(RL1.map_dict.keys())
print(RL1.combine_levels(RL2))
print(RL1.map_dict[1] is RL2.map_dict[0.95])
print(RL1+RL2)
print(-RL1)

# 71
# 330
# -5
# <class 'input.integer.Integer'>
# {1: Integer(5), 0.8: Integer(66), 0.4: Integer(10)}
# dict_keys([1, 0.8, 0.4])
# [1, 0.95, 0.8, 0.4, 0.2, 0.1]
# False
# {1: Integer(-12), 0.95: Integer(10), 0.8: Integer(71), 0.4: Integer(15), 0.2: Integer(20), 0.1: Integer(15)}
# {1: Integer(-5), 0.8: Integer(-66), 0.4: Integer(-10)}