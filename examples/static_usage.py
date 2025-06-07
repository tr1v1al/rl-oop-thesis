from examples.static_output import A,B,RLA,RLB

rla1, rla2 = RLA({1: A(5), 0.8: A(7)}), RLA({1: A(10), 0.7: A(6)})
print(rla1+rla2)
# RL-A
# Level | Object
# ------+-------
# 1     | 15
# 0.8   | 17
# 0.7   | 13

rlb1, rlb2 = RLB({1: B(5), 0.8: B(7)}), RLB({1: B(10), 0.7: B(6)})
print(rlb1.combine(rlb2))
# RL-A
# Level | Object
# ------+-------
# 1     | 16
# 0.8   | 18
# 0.7   | 14

print(rlb1.combine(rlb2, y=rla1, random_param=rla2))
# RL-A
# Level | Object
# ------+-------
# 1     | 30
# 0.8   | 34
# 0.7   | 26

print(rlb1.combine(rlb2, y=rlb2))
# TypeError: Error in RLB at level 1: y must be of class A