class A:
    def __init__(self, val):
        self.val = val
    def __add__(self, other):
        return A(self.val+other.val)
    def __str__(self):
        return str(self.val)
class B:
    def __init__(self, val):
        self.val = val
    def combine(self, other, y=A(1)):
        if not isinstance(y, A):
            raise TypeError("y must be of class A")
        return A(self.val+other.val+y.val)
    def __str__(self):
        return str(self.val)