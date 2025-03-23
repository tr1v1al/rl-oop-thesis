from input.integer import Integer
from expected.rl_integer_expected import RLInteger
#from output.rl_integer import RLInteger

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