import unittest
from rlistic.runtime import rlify, RL_REGISTRY

# Custom class with method with complicated signatures
class ComplicatedClass:
    def __init__(self, val):
        self.val = val
    def method(self, a, /, b : int = 7, *args: tuple[int], c:int, **kwargs: dict[str,int]):
        """
        Complicated method with positional-only args (a), args with default params (b),
        arbitrary positional args, keyword only args (c), and arbitrary kwargs
        """
        return self.val+a.val+b+c+sum(args)+sum(kwargs.values())

# Child class to test inheritance
class ChildClass(ComplicatedClass):
    pass

class TestRuntime(unittest.TestCase):
    def setUp(self):
        # Built-in int and set
        RLint, RLset = rlify(int), rlify(set)
        self.rlint1 = RLint({1: 5, 0.8: 3})
        self.rlint2 = RLint({1: 5, 0.7 : 4})
        self.rlset1 = RLset({1: {'a','b'}, 0.8: {'c'}})
        self.rlset2 = RLset({1: {'c'}, 0.7 : {'a','c','d'}})
        # Custom class
        RLComplicatedClass = rlify(ComplicatedClass)
        self.rlcomp1 = RLComplicatedClass({1: ComplicatedClass(5), 0.8: ComplicatedClass(10)})
        self.rlcomp2 = RLComplicatedClass({1: ComplicatedClass(3), 0.7: ComplicatedClass(2)})

    def test_regular_methods(self):
        """Test regular methods"""
        RLset = rlify(set)
        union = self.rlset1.union(self.rlset2)
        exp_union = {1: {'a','b','c'}, 0.8: {'c'}, 0.7: {'a','c','d'}}
        self.assertIsInstance(union, RLset)
        self.assertEqual(union.mapping, exp_union)

    def test_magic_methods(self):
        """Test magic methods""" 
        RLint, RLset = rlify(int), rlify(set)
        # Add RL-ints
        sum = self.rlint1+self.rlint2
        exp_sum = {1: 10, 0.8: 8, 0.7: 7}
        self.assertIsInstance(sum, RLint)
        self.assertEqual(sum.mapping, exp_sum)
        # Union of RL-sets
        union = self.rlset1 | self.rlset2
        exp_union = {1: {'a','b','c'}, 0.8: {'c'}, 0.7: {'a','c','d'}}
        self.assertIsInstance(union, RLset)
        self.assertEqual(union.mapping, exp_union)

    def test_crisp_arguments(self):
        """Test passing crisp arguments"""
        RLint, RLset = rlify(int), rlify(set)
        # Add RL-ints
        sum = self.rlint1+10
        exp_sum = {1: 15, 0.8: 13}
        self.assertIsInstance(sum, RLint)
        self.assertEqual(sum.mapping, exp_sum)
        # Union of RL-sets
        union = self.rlset1 | {'b','c'}
        exp_union = {1: {'a','b','c'}, 0.8: {'b','c'}}
        self.assertIsInstance(union, RLset)
        self.assertEqual(union.mapping, exp_union)

    def test_squashing(self):
        """Test squashing RLs"""
        RLint, RLset = rlify(int), rlify(set)
        # Subtraction of RL-ints
        sub = RLint({1: 7, 0.8: 3, 0.5: 5}) - RLint({1: 5, 0.8: 1, 0.6: 10})
        exp_sub = {1: 2, 0.6: -7, 0.5: -5}
        self.assertIsInstance(sub, RLint)
        self.assertEqual(sub.mapping, exp_sub)
        # Intersection of RL-sets
        union = self.rlset1 & self.rlset2
        exp_union = {1: set(), 0.8: {'c'}}
        self.assertIsInstance(union, RLset)
        self.assertEqual(union.mapping, exp_union)

    def test_crisp_output(self):
        """"Test giving crisp output"""
        # Multiplication of RL-ints
        RLint = rlify(int)
        mult = RLint({1: 5, 0.8: 3}) * RLint({1: 3, 0.8: 5})
        exp_mult = 15
        self.assertIsInstance(mult, int)
        self.assertEqual(mult, exp_mult)

    def test_output_class(self):
        """"Test different class of the output"""
        # Division of RL-ints produces RL-float
        RLint = rlify(int)
        div = RLint({1: 10, 0.8: 8}) / RLint({1: 5, 0.8: 2})
        exp_div = {1: 2, 0.8: 4}
        RLfloat = rlify(float)
        self.assertIsInstance(div, RLfloat)
        self.assertEqual(div._instance_class, float)
        self.assertEqual(div.mapping, exp_div)

    def test_method_signatures(self):
        """"Test complicated method signatures"""
        # Test default value
        RLint = rlify(int)
        def_test = self.rlcomp1.method(self.rlcomp2, c=self.rlint1)
        exp = {1: 20, 0.8: 23, 0.7: 22}
        self.assertIsInstance(def_test, RLint)
        self.assertEqual(def_test._instance_class, int)
        self.assertEqual(def_test.mapping, exp)
        # General test with arbirtrary args and kwargs
        def_test = self.rlcomp1.method(self.rlcomp2, 10, 20, c=self.rlint1, some_kwarg=10)
        exp = {1: 53, 0.8: 56, 0.7: 55}
        self.assertIsInstance(def_test, RLint)
        self.assertEqual(def_test._instance_class, int)
        self.assertEqual(def_test.mapping, exp)

    def test_inheritance(self):
        """Test inherited method calling"""
        RLChildClass, RLint = rlify(ChildClass), rlify(int)
        rlchild1 = RLChildClass({1: ChildClass(5), 0.8: ChildClass(10)})
        rlchild2 = RLChildClass({1: ChildClass(3), 0.7: ChildClass(2)})
        def_test = rlchild1.method(rlchild2, c=self.rlint1)
        exp = {1: 20, 0.8: 23, 0.7: 22}
        self.assertIsInstance(def_test, RLint)
        self.assertEqual(def_test._instance_class, int)
        self.assertEqual(def_test.mapping, exp)

    def test_explicit_magic_methods(self):
        """"Test explicit magic methods"""
        # Not equality of RL-ints
        RLbool = rlify(bool)
        neq = self.rlint1.__ne__(self.rlint2)
        exp_neq = {1: False, 0.8: True}
        self.assertIsInstance(neq, RLbool)
        self.assertEqual(neq.mapping, exp_neq)

if __name__ == '__main__':
    unittest.main()