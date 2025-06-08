from rlistic.proxy import RL, add_magic_methods

# RL-integers
rla_int1, rla_int2 = RL({1: 3, 0.6: 2}), RL({1: 7, 0.6: 5})
print(rla_int1+rla_int2)
# RL-int
# Level | Object
# ------+-------
# 1     | 10
# 0.6   | 7

# RL-sets
rla_set1 = RL({1: {5,3,2}, 0.7: {1,2,7}})
rla_set2 = RL({1: {1,6,7}, 0.6: {9,4,10}})
rl_inter = rla_set1 & rla_set2
rl_union = rla_set1 | rla_set2
print(rl_inter)
# RL-set
# Level | Object
# ------+---------
# 1     | set()
# 0.7   | {1, 7}
# 0.6   | set()
print(rl_union)
# RL-set
# Level | Object
# ------+----------------------
# 1     | {1, 2, 3, 5, 6, 7}
# 0.7   | {1, 2, 6, 7}
# 0.6   | {1, 2, 4, 7, 9, 10}

add_magic_methods(['__pow__'])
print(rla_int1**rla_int2)
# RL-int
# Level | Object
# ------+-------
# 1     | 2187
# 0.6   | 32