import unittest
from rlistic.proxy import RL, add_magic_methods

# Custom set class for testing RL operations
class MySet(set):
    def __add__(self, other):
        return MySet(self.union(other))

class TestProxy(unittest.TestCase):
    def setUp(self):
        # Valid RL mappings with MySet
        self.mapping1 = {1.0: MySet({"a", "b"}), 0.7: MySet({"a", "c"})}
        self.mapping2 = {1.0: MySet({"b", "c"}), 0.8: MySet({"c"})}
        # Invalid mappings
        self.invalid_mapping = {0.8: MySet({"a"}), 0.5: MySet({"b"})}
        self.mixed_mapping = {1.0: "a", 0.8: MySet({"b"})}
        # Create RL instances
        self.rl1 = RL(self.mapping1)
        self.rl2 = RL(self.mapping2)

    def test_rl_init(self):
        """Test RL initialization."""
        self.assertEqual(self.rl1.mapping, self.mapping1)
        self.assertEqual(self.rl1.instance_class, MySet)
        with self.assertRaises(ValueError):
            RL(self.invalid_mapping)
        with self.assertRaises(TypeError):
            RL(self.mixed_mapping)

    def test_level_set(self):
        """Test level_set method."""
        self.assertEqual(self.rl1.level_set(), [1.0, 0.7])
        self.assertEqual(self.rl2.level_set(), [1.0, 0.8])

    def test_get_object(self):
        """Test get_object method."""
        self.assertEqual(self.rl1.get_object(1.0), MySet({"a", "b"}))
        self.assertEqual(self.rl1.get_object(0.7), MySet({"a", "c"}))
        self.assertIsNone(self.rl1.get_object(0.5))
        self.assertEqual(self.rl1.get_object(0.5, MySet()), MySet())

    def test_instance_class_property(self):
        """Test instance_class property."""
        self.assertEqual(self.rl1.instance_class, MySet)

    def test_mapping_property(self):
        """Test mapping property."""
        self.assertEqual(self.rl1.mapping, self.mapping1)

    def test_combine_levels(self):
        """Test __combine_levels method."""
        levels = self.rl1._RL__combine_levels(self.rl2)
        self.assertEqual(levels, [1.0, 0.8, 0.7])

    def test_general_method(self):
        """Test general_method with __add__."""
        result = self.rl1.general_method("__add__", self.rl2)
        expected = {1.0: MySet({"a", "b", "c"}), 0.7: MySet({"a", "c"})}
        self.assertIsInstance(result, RL)
        self.assertEqual(result.mapping, expected)

    def test_magic_method(self):
        """Test magic method __add__."""
        result = self.rl1 + self.rl2
        expected = {1.0: MySet({"a", "b", "c"}), 0.7: MySet({"a", "c"})}
        self.assertIsInstance(result, RL)
        self.assertEqual(result.mapping, expected)

    def test_dynamic_dispatch(self):
        """Test __getattr__ for dynamic method dispatch."""
        result = self.rl1.union(self.rl2)
        expected = {1.0: MySet({"a", "b", "c"}), 0.7: MySet({"a", "c"})}
        self.assertIsInstance(result, RL)
        self.assertEqual(result.mapping, expected)

    def test_add_magic_methods(self):
        """Test add_magic_methods function."""
        add_magic_methods(["__eq__"])
        self.assertTrue(hasattr(RL, "__eq__"))
        rl3 = RL({1.0: MySet({"a", "b"}), 0.7: MySet({"a", "c"})})
        result = self.rl1 == rl3
        #self.assertIsInstance(result, RL)
        self.assertEqual(result, True)
        with self.assertRaises(TypeError):
            add_magic_methods("not a list")
        with self.assertRaises(TypeError):
            add_magic_methods(["__eq__", 123])
        with self.assertRaises(ValueError):
            add_magic_methods(["invalid"])

if __name__ == "__main__":
    unittest.main()