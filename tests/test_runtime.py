import unittest
from rlistic.runtime import rlify, RL_REGISTRY

class A:
    def __init__(self, val):
        self.val = val
    
    def __add__(self, other):
        return A(self.val + other.val)
    
    def __sub__(self, other):
        return self.val - other.val

class MySet(set):
    def union(self, other):
        return OtherSet(set.union(self, other))

class OtherSet(set):
    pass

class TestStatic(unittest.TestCase):
    def setUp(self):
        # Clear RL_REGISTRY before each test to avoid interference
        RL_REGISTRY.clear()

    def test_instantiation(self):
        """Test RLA instantiation with valid mapping and _instance_class."""
        RLA = rlify(A)
        rla = RLA({1.0: A(10), 0.8: A(3)})
        self.assertEqual(RLA._instance_class, A)
        #self.assertEqual(rla.mapping, {1.0: A(10), 0.8: A(3)})
        self.assertIsInstance(rla, RLA)
        self.assertIn(A, RL_REGISTRY)

    def test_type_validation(self):
        """Test TypeError for mappings with incorrect types."""
        RLA = rlify(A)
        with self.assertRaises(TypeError):
            RLA({1.0: MySet({"a"}), 0.8: A(3)})  # Wrong type
        with self.assertRaises(TypeError):
            RLA({1.0: "invalid", 0.8: A(3)})  # Non-A object

    def test_add_operation(self):
        """Test __add__ operation returning RLA."""
        RLA = rlify(A)
        rla1 = RLA({1.0: A(10), 0.8: A(3)})
        rla2 = RLA({1.0: A(5), 0.7: A(2)})
        result = rla1 + rla2
        self.assertIsInstance(result, RLA)
        self.assertEqual(result.mapping[1.0].val, 15)  # 10 + 5
        self.assertEqual(result.mapping[0.8].val, 8)   # 3 + 2
        self.assertEqual(result.mapping[0.7].val, 5)   # 3 + 2 (extended)

    def test_sub_operation(self):
        """Test __sub__ operation returning crisp int."""
        RLA = rlify(A)
        rla1 = RLA({1.0: A(10), 0.7: A(7)})
        rla2 = RLA({1.0: A(5), 0.7: A(2)})
        result = rla1 - rla2
        self.assertIsInstance(result, int)
        self.assertEqual(result, 5)  # 10 - 5 (level 1.0)

    def test_dynamic_rl_creation(self):
        """Test dynamic RL class creation for OtherSet."""
        RLMySet = rlify(MySet)
        rl1 = RLMySet({1.0: MySet({"a"}), 0.7: MySet({"b"})})
        rl2 = RLMySet({1.0: MySet({"c"}), 0.7: MySet({"d"})})
        result = rl1.union(rl2)
        self.assertIsInstance(result, RL_REGISTRY[OtherSet])
        self.assertEqual(result.mapping, {1.0: OtherSet({"a", "c"}), 0.7: OtherSet({"b", "d"})})
        self.assertIn(OtherSet, RL_REGISTRY)

    def test_single_level_mapping(self):
        """Test single-level mapping returns crisp object."""
        RLA = rlify(A)
        rla = RLA({1.0: A(10)})
        result = rla + RLA({1.0: A(5)})
        self.assertIsInstance(result, A)
        self.assertEqual(result.val, 15)

    def test_str_representation(self):
        """Test __str__ uses rl_table correctly."""
        RLA = rlify(A)
        rla = RLA({1.0: A(10), 0.8: A(3)})
        self.assertIn("A", str(rla))
        self.assertIn("1.0", str(rla))
        self.assertIn("0.8", str(rla))

    def test_crisp_argument_rlification(self):
        """Test RLification of crisp arguments in general_method."""
        RLA = rlify(A)
        rla = RLA({1.0: A(10), 0.8: A(3)})
        crisp_arg = A(5)
        result = rla + crisp_arg
        self.assertIsInstance(result, RLA)
        self.assertEqual(result.mapping[1.0].val, 15)  # 10 + 5
        self.assertEqual(result.mapping[0.8].val, 8)   # 3 + 5

    def test_invalid_mapping(self):
        """Test invalid mapping raises ValueError."""
        RLA = rlify(A)
        with self.assertRaises(ValueError):
            RLA({0.5: A(10)})  # Missing level 1.0
        with self.assertRaises(ValueError):
            RLA({1.0: A(10), 1.5: A(3)})  # Level > 1.0

    def test_builtin_type(self):
        """Test rlification of built-in type (int)."""
        RLInt = rlify(int)
        rlint = RLInt({1.0: 10, 0.8: 3})
        result = rlint + RLInt({1.0: 5, 0.7: 2})
        self.assertIsInstance(result, RLInt)
        self.assertEqual(result.mapping, {1.0: 15, 0.8: 8, 0.7: 5})

if __name__ == '__main__':
    unittest.main()