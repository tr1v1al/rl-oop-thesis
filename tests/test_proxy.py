import unittest
from rlistic.proxy import RL, add_magic_methods

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

class TestProxy(unittest.TestCase):
    def setUp(self):
        # Built-in int and set
        self.rlint1 = RL({1: 5, 0.8: 3})
        self.rlint2 = RL({1: 5, 0.7 : 4})
        self.rlset1 = RL({1: {'a','b'}, 0.8: {'c'}})
        self.rlset2 = RL({1: {'c'}, 0.7 : {'a','c','d'}})
        # Custom class
        self.rlcomp1 = RL({1: ComplicatedClass(5), 0.8: ComplicatedClass(10)})
        self.rlcomp2 = RL({1: ComplicatedClass(3), 0.7: ComplicatedClass(2)})

    def test_regular_methods(self):
        """Test regular methods"""
        union = self.rlset1.union(self.rlset2)
        exp_union = {1: {'a','b','c'}, 0.8: {'c'}, 0.7: {'a','c','d'}}
        self.assertIsInstance(union, RL)
        self.assertEqual(union.mapping, exp_union)

    def test_magic_methods(self):
        """Test magic methods""" 
        # Add RL-ints
        sum = self.rlint1+self.rlint2
        exp_sum = {1: 10, 0.8: 8, 0.7: 7}
        self.assertIsInstance(sum, RL)
        self.assertEqual(sum.mapping, exp_sum)
        # Union of RL-sets
        union = self.rlset1 | self.rlset2
        exp_union = {1: {'a','b','c'}, 0.8: {'c'}, 0.7: {'a','c','d'}}
        self.assertIsInstance(union, RL)
        self.assertEqual(union.mapping, exp_union)

    def test_crisp_arguments(self):
        """Test passing crisp arguments"""
        # Add RL-ints
        sum = self.rlint1+10
        exp_sum = {1: 15, 0.8: 13}
        self.assertIsInstance(sum, RL)
        self.assertEqual(sum.mapping, exp_sum)
        # Union of RL-sets
        union = self.rlset1 | {'b','c'}
        exp_union = {1: {'a','b','c'}, 0.8: {'b','c'}}
        self.assertIsInstance(union, RL)
        self.assertEqual(union.mapping, exp_union)

    def test_squashing(self):
        """Test squashing RLs"""
        # Subtraction of RL-ints
        sub = RL({1: 7, 0.8: 3, 0.5: 5}) - RL({1: 5, 0.8: 1, 0.6: 10})
        exp_sub = {1: 2, 0.6: -7, 0.5: -5}
        self.assertIsInstance(sub, RL)
        self.assertEqual(sub.mapping, exp_sub)
        # Intersection of RL-sets
        union = self.rlset1 & self.rlset2
        exp_union = {1: set(), 0.8: {'c'}}
        self.assertIsInstance(union, RL)
        self.assertEqual(union.mapping, exp_union)

    def test_crisp_output(self):
        """"Test giving crisp output"""
        # Multiplication of RL-ints
        mult = RL({1: 5, 0.8: 3}) * RL({1: 3, 0.8: 5})
        exp_mult = 15
        self.assertIsInstance(mult, int)
        self.assertEqual(mult, exp_mult)

    def test_output_class(self):
        """"Test different class of the output"""
        # Division of RL-ints produces RL-float
        div = RL({1: 10, 0.8: 8}) / RL({1: 5, 0.8: 2})
        exp_div = {1: 2, 0.8: 4}
        self.assertIsInstance(div, RL)
        self.assertEqual(div.instance_class, float)
        self.assertEqual(div.mapping, exp_div)

    def test_method_signatures(self):
        """"Test complicated method signatures"""
        # Test default value
        def_test = self.rlcomp1.method(self.rlcomp2, c=self.rlint1)
        exp = {1: 20, 0.8: 23, 0.7: 22}
        self.assertIsInstance(def_test, RL)
        self.assertEqual(def_test.instance_class, int)
        self.assertEqual(def_test.mapping, exp)
        # General test with arbirtrary args and kwargs
        def_test = self.rlcomp1.method(self.rlcomp2, 10, 20, c=self.rlint1, some_kwarg=10)
        exp = {1: 53, 0.8: 56, 0.7: 55}
        self.assertIsInstance(def_test, RL)
        self.assertEqual(def_test.instance_class, int)
        self.assertEqual(def_test.mapping, exp)

    def test_inheritance(self):
        """Test inherited method calling"""
        rlchild1 = RL({1: ChildClass(5), 0.8: ChildClass(10)})
        rlchild2 = RL({1: ChildClass(3), 0.7: ChildClass(2)})
        def_test = rlchild1.method(rlchild2, c=self.rlint1)
        exp = {1: 20, 0.8: 23, 0.7: 22}
        self.assertIsInstance(def_test, RL)
        self.assertEqual(def_test.instance_class, int)
        self.assertEqual(def_test.mapping, exp)

    def test_explicit_magic_methods(self):
        """"Test explicit magic methods not defined for RL"""
        # Modulus of RL-ints
        neq = self.rlint1.__mod__(self.rlint2)
        exp_neq = {1: 0, 0.8: 3}
        self.assertIsInstance(neq, RL)
        self.assertEqual(neq.mapping, exp_neq)

    def test_add_magic_methods(self):
        """Test add_magic_methods function."""
        self.assertFalse(hasattr(RL, "__pow__"))
        add_magic_methods(["__pow__"])
        self.assertTrue(hasattr(RL, "__pow__"))
        pow = self.rlint1**self.rlint2
        exp_pow = {1: 3125, 0.8: 243, 0.7: 81}
        self.assertIsInstance(pow, RL)
        self.assertEqual(pow.mapping, exp_pow)
        with self.assertRaises(TypeError):
            add_magic_methods("not a list")
        with self.assertRaises(TypeError):
            add_magic_methods(["__eq__", 123])
        with self.assertRaises(ValueError):
            add_magic_methods(["invalid"])

if __name__ == "__main__":
    unittest.main()