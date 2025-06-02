class A:
    def __init__(self, val):
        self.val = val
    def __add__(self, other):
        return A(self.val+other.val)
    def add(self, other, x=1):
        return A(self.val+other.val+x)
    def __str__(self):
        return str(self.val)
class B:
    def __init__(self, val):
        self.val = val
    def combine(self, other, *args, y=2, **kwargs):
        return B(self.val+other.val+y+sum(args)+sum(kwargs.values))
    def __str__(self):
        return str(self.val)