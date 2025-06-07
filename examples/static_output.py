from rlistic.static import _RLBase, RL_REGISTRY

class A:

    def __init__(self, val):
        self.val = val

    def __add__(self, other):
        return A(self.val + other.val)

    def __str__(self):
        return str(self.val)
class B:

    def __init__(self, val):
        self.val = val

    def combine(self, other, y=A(1), *args, **kwargs):
        """"
        Method with a complicated signature that returns
        an object of another class
        """
        if not isinstance(y, A):
            raise TypeError('y must be of class A')
        arg_sum = sum([arg.val for arg in args])
        kwarg_sum = sum([kwarg.val for kwarg in kwargs.values()])
        return A(self.val + other.val + y.val + arg_sum + kwarg_sum)

    def __str__(self):
        return str(self.val)

class RLA(_RLBase):
    _instance_class = A

    def __add__(self, other):
        return self.general_method('__add__', other)
class RLB(_RLBase):
    _instance_class = B

    def combine(self, other, y=A(1), *args, **kwargs):
        return self.general_method('combine', other, y, *args, **kwargs)

RL_REGISTRY[A] = RLA
RL_REGISTRY[B] = RLB