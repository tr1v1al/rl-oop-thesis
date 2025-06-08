from rlistic.runtime import rlify

class A:
    def __init__(self, val):
        self.val = val

    def __add__(self, other):   # Addition of objects of A
        return A(self.val+other.val)

    def __mul__(self, other):   # Multiplication with an integer
        return A(self.val*other)

    def __sub__(self, other):   # Returning a float
        return 1.0 * (self.val - other.val)
    
    def __str__(self):
        return str(self.val)

RLA = rlify(A)
rla1 = RLA({1: A(10), 0.8: A(3)})
rla2 = RLA({1: A(5), 0.7: A(7)})

print(rla1+rla2)    # Regular addition of RLA objects
# RL-A
# Level | Object
# ------+-------
# 1     | 15
# 0.8   | 8
# 0.7   | 10

print(rla1*10)      # Passing crisp integer creates RLint as side effect
# RL-A
# Level | Object
# ------+-------
# 1     | 100
# 0.8   | 30

print(rla1 - rla2)  # Returning an RL float creates RLfloat as side effect
# RL-float
# Level | Object
# ------+-------
# 1     | 5.0
# 0.8   | -2.0
# 0.7   | -4.0

RLint = rlify(int)  # Obtain RLint, which already exists

rlint1 = RLint({1:10, 0.8: 5})
rlint2 = RLint({1:5, 0.7: 3})

print(rlint1*rlint2)    # RLint extends all of int's methods
# RL-int
# Level | Object
# ------+-------
# 1     | 50
# 0.8   | 25
# 0.7   | 15