import unittest
import os
import tempfile
from pathlib import Path
from typing import Set
from rlistic.common import validate_level_set, validate_mapping, rl_table, rl_input, fuzzy_to_rl, rl_fuzzy_summary

class TestCommon(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

        # Create valid input file
        self.input_file = os.path.join(self.temp_path, "inputs.txt")
        with open(self.input_file, "w") as f:
            f.write("1 0.8\ninput1\ninput2\n")

        # Create invalid input file (empty)
        self.empty_file = os.path.join(self.temp_path, "empty.txt")
        with open(self.empty_file, "w") as f:
            pass

        # Create invalid input file (mismatched inputs)
        self.mismatch_file = os.path.join(self.temp_path, "mismatch.txt")
        with open(self.mismatch_file, "w") as f:
            f.write("1 0.8\ninput1\n")

    def tearDown(self):
        # Cleanup handled by TemporaryDirectory
        self.temp_dir.cleanup()

    def test_validate_level_set(self):
        """Test validate_level_set for valid and invalid level sets."""
        # Valid
        validate_level_set([1.0, 0.8, 0.5])
        # Invalid: not a list
        with self.assertRaises(TypeError):
            validate_level_set({1.0, 0.8})
        # Invalid: empty
        with self.assertRaises(ValueError):
            validate_level_set([])
        # Invalid: missing 1
        with self.assertRaises(ValueError):
            validate_level_set([0.8, 0.5])
        # Invalid: not numbers
        with self.assertRaises(TypeError):
            validate_level_set([1.0, "0.8"])
        # Invalid: out of range
        with self.assertRaises(ValueError):
            validate_level_set([1.0, 1.1])
        with self.assertRaises(ValueError):
            validate_level_set([1.0, 0.0])
        # Invalid: not descending
        with self.assertRaises(ValueError):
            validate_level_set([1.0, 0.5, 0.8])

    def test_validate_mapping(self):
        """Test validate_mapping for valid and invalid mappings."""
        # Valid
        validate_mapping({1.0: "a", 0.8: "b"})
        validate_mapping({1.0: {1}, 0.8: {2}})
        # Invalid: not a dict
        with self.assertRaises(TypeError):
            validate_mapping([1.0, 0.8])
        # Invalid: invalid level-set
        with self.assertRaises(ValueError):
            validate_mapping({0.8: "a", 0.5: "b"})
        # Invalid: mixed types
        with self.assertRaises(TypeError):
            validate_mapping({1.0: "a", 0.8: 1})

    def test_rl_table(self):
        """Test rl_table formatting."""
        mapping = {1.0: "input1", 0.8: "input2"}
        table = rl_table("Test", mapping)
        expected = (
            "RL-Test\n"
            "Level | Object  \n"
            "------+---------\n"
            "1.0   | input1  \n"
            "0.8   | input2  "
        )
        self.assertEqual(table, expected)

    def test_rl_input(self):
        """Test rl_input with valid and invalid files."""
        # Valid without processing
        result = rl_input(self.input_file)
        self.assertEqual(result, {1.0: "input1", 0.8: "input2"})
        # Valid with processing
        result = rl_input(self.input_file, lambda x: x.upper())
        self.assertEqual(result, {1.0: "INPUT1", 0.8: "INPUT2"})
        # Invalid: file not found
        with self.assertRaises(ValueError):
            rl_input(os.path.join(self.temp_path, "nonexistent.txt"))
        # Invalid: empty file
        with self.assertRaises(ValueError):
            rl_input(self.empty_file)
        # Invalid: non-float levels
        with open(os.path.join(self.temp_path, "bad_levels.txt"), "w") as f:
            f.write("a b\ninput1\ninput2\n")
        with self.assertRaises(ValueError):
            rl_input(os.path.join(self.temp_path, "bad_levels.txt"))
        # Invalid: mismatched inputs
        with self.assertRaises(ValueError):
            rl_input(self.mismatch_file)

    def test_fuzzy_to_rl(self):
        """Test fuzzy_to_rl conversion."""
        fuzzy_set = {"a": 0.8, "b": 0.7}
        result = fuzzy_to_rl(fuzzy_set)
        expected = {1.0: set(), 0.8: {"a"}, 0.7: {"a", "b"}}
        self.assertEqual(result, expected)
        # Empty fuzzy set
        result = fuzzy_to_rl({})
        self.assertEqual(result, {1.0: set()})

    def test_rl_fuzzy_summary(self):
        """Test rl_fuzzy_summary computation."""
        rl = {1.0: {"a", "b"}, 0.7: {"a", "c"}, 0.1: {"b"}}
        result = rl_fuzzy_summary(rl)
        expected = {"a": 0.9, "c": 0.6, "b": 0.4}
        self.assertEqual(result, expected)
        # Empty RL
        with self.assertRaises(ValueError):
            rl_fuzzy_summary({})
        # Invalid levels
        with self.assertRaises(ValueError):
            rl_fuzzy_summary({1.1: {"a"}})

if __name__ == "__main__":
    unittest.main()