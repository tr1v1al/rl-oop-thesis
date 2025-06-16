import unittest
import tempfile
import os
import importlib.util
import sys
import re
from rlistic.static import transform_file, RL_REGISTRY

# Input class code for transformation tests
SAMPLE_CLASS_CODE = """
class A:
    def __init__(self, val):
        self.val = val
    def __add__(self, other):
        return A(self.val + other.val)
    def __str__(self):
        return str(self.val)
    def __eq__(self, other):
        return self.val == other.val

class B:
    def __init__(self, val):
        self.val = val
    def combine(self, other, y=A(1), *args, c, **kwargs):
        if not isinstance(y, A):
            raise TypeError("y must be of class A")
        arg_sum = sum([arg.val for arg in args])
        kwarg_sum = sum([kwarg.val for kwarg in kwargs.values()])
        return A(self.val + other.val + y.val + arg_sum + c.val + kwarg_sum)
    def __str__(self):
        return str(self.val)
    def __eq__(self, other):
        return self.val == other.val
"""

# Expected output code for transformation tests and functional tests
PRE_GENERATED_RL_CODE = """
from rlistic.static import _RLBase, RL_REGISTRY

class A:
    def __init__(self, val):
        self.val = val
    def __add__(self, other):
        return A(self.val + other.val)
    def __str__(self):
        return str(self.val)
    def __eq__(self, other):
        return self.val == other.val

class B:
    def __init__(self, val):
        self.val = val
    def combine(self, other, y=A(1), *args, c, **kwargs):
        if not isinstance(y, A):
            raise TypeError("y must be of class A")
        arg_sum = sum([arg.val for arg in args])
        kwarg_sum = sum([kwarg.val for kwarg in kwargs.values()])
        return A(self.val + other.val + y.val + arg_sum + c.val + kwarg_sum)
    def __str__(self):
        return str(self.val)
    def __eq__(self, other):
        return self.val == other.val

class RLA(_RLBase):
    _instance_class = A
    def __add__(self, other):
        return self.general_method('__add__', other)
    def __eq__(self, other):
        return self.general_method('__eq__', other)

class RLB(_RLBase):
    _instance_class = B
    def combine(self, other, y=A(1), *args, c, **kwargs):
        return self.general_method('combine', other, y, *args, c=c, **kwargs)
    def __eq__(self, other):
        return self.general_method('__eq__', other)

RL_REGISTRY[A] = RLA
RL_REGISTRY[B] = RLB
"""

class TestStatic(unittest.TestCase):
    def setUp(self):
        """Set up temporary files for transformation tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.temp_dir.name, "input.py")
        self.output_file = os.path.join(self.temp_dir.name, "output.py")
        with open(self.input_file, "w") as f:
            f.write(SAMPLE_CLASS_CODE.strip())

    def setUpRLClasses(self):
        """Set up RL-classes from pre-generated code for functional tests."""
        with open(self.output_file, "w") as f:
            f.write(PRE_GENERATED_RL_CODE.strip())
        spec = importlib.util.spec_from_file_location("output", self.output_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["output"] = module
        spec.loader.exec_module(module)
        self.RLA = RL_REGISTRY[module.A]
        self.RLB = RL_REGISTRY[module.B]
        self.rla1 = self.RLA({1.0: module.A(5), 0.8: module.A(3)})
        self.rla2 = self.RLA({1.0: module.A(2), 0.7: module.A(4)})
        self.rlb1 = self.RLB({1.0: module.B(5), 0.8: module.B(10)})
        self.rlb2 = self.RLB({1.0: module.B(3), 0.7: module.B(2)})

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def normalize_code(self, code):
        """Normalize code by removing extra whitespace and standardizing quotes."""
        # Replace multiple newlines with single, strip leading/trailing whitespace
        code = re.sub(r'\n+', '\n', code.strip())
        # Replace double quotes with single quotes for consistency
        code = code.replace('"', "'")
        # Remove trailing whitespace per line
        code = '\n'.join(line.rstrip() for line in code.split('\n'))
        return code

    def test_transform_file(self):
        """Test transform_file generates the correct output for the given input."""
        transform_file(self.input_file, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))
        with open(self.output_file, "r") as f:
            content = f.read()
        content_normalized = self.normalize_code(content)
        expected_normalized = self.normalize_code(PRE_GENERATED_RL_CODE)
        self.assertEqual(content_normalized, expected_normalized, "Output file content does not match expected RL-class code")

    def test_invalid_input(self):
        """Test transform_file handles invalid inputs."""
        with open(self.input_file, "w") as f:
            f.write("")
        with self.assertRaises(ValueError):
            transform_file(self.input_file, self.output_file)
        with open(self.input_file, "w") as f:
            f.write("class InvalidClass: pass; invalid syntax")
        with self.assertRaises(SyntaxError):
            transform_file(self.input_file, self.output_file)
        with self.assertRaises(FileNotFoundError):
            transform_file("nonexistent.py", self.output_file)

    def test_regular_methods(self):
        """Test regular methods of RL-classes."""
        self.setUpRLClasses()
        result = self.rlb1.combine(self.rlb2, c=self.rla1)
        expected = {1.0: self.rla1._instance_class(14), 0.8: self.rla1._instance_class(17), 0.7: self.rla1._instance_class(16)}
        self.assertIsInstance(result, self.RLA)
        self.assertEqual({k: v.val for k, v in result.mapping.items()}, {k: v.val for k, v in expected.items()})

    def test_magic_methods(self):
        """Test magic methods of RL-classes."""
        self.setUpRLClasses()
        result = self.rla1 + self.rla2
        expected = {1.0: self.rla1._instance_class(7), 0.8: self.rla1._instance_class(5), 0.7: self.rla1._instance_class(7)}
        self.assertIsInstance(result, self.RLA)
        self.assertEqual({k: v.val for k, v in result.mapping.items()}, {k: v.val for k, v in expected.items()})

    def test_crisp_arguments(self):
        """Test RL-classes with crisp arguments."""
        self.setUpRLClasses()
        crisp_obj = self.rla1._instance_class(10)
        result = self.rla1 + crisp_obj
        expected = {1.0: self.rla1._instance_class(15), 0.8: self.rla1._instance_class(13)}
        self.assertIsInstance(result, self.RLA)
        self.assertEqual({k: v.val for k, v in result.mapping.items()}, {k: v.val for k, v in expected.items()})

    def test_squashing(self):
        """Test squashing behavior when levels produce identical results."""
        self.setUpRLClasses()
        result = self.rla1 + self.rla1._instance_class(0)
        expected = {1.0: self.rla1._instance_class(5), 0.8: self.rla1._instance_class(3)}
        self.assertIsInstance(result, self.RLA)
        self.assertEqual({k: v.val for k, v in result.mapping.items()}, {k: v.val for k, v in expected.items()})

    def test_crisp_output(self):
        """Test crisp output when results are identical across levels."""
        self.setUpRLClasses()
        result = self.rla1 + self.RLA({1: self.rla1._instance_class(-5), 0.8: self.rla1._instance_class(-3)})
        expected = 0
        self.assertIsInstance(result, self.rla1._instance_class)
        self.assertEqual(result.val, expected)

    def test_output_class(self):
        """Test correct output class for RL operations."""
        self.setUpRLClasses()
        result = self.rlb1.combine(self.rlb2, c=self.rla1)
        self.assertIsInstance(result, self.RLA)
        self.assertEqual(result._instance_class, self.rla1._instance_class)

    def test_method_signatures(self):
        """Test complex method signatures in RL-classes."""
        self.setUpRLClasses()
        result = self.rlb1.combine(self.rlb2, y=self.rla1, c=self.rla2, extra=self.rla1)
        expected = {1.0: self.rla1._instance_class(20), 0.8: self.rla1._instance_class(21), 0.7: self.rla1._instance_class(22)}
        self.assertIsInstance(result, self.RLA)
        self.assertEqual({k: v.val for k, v in result.mapping.items()}, {k: v.val for k, v in expected.items()})

    def test_type_checking(self):
        """Test type checking for RL-class instantiation."""
        self.setUpRLClasses()
        invalid_obj = int(5)
        with self.assertRaises(TypeError):
            self.RLA({1.0: invalid_obj})

if __name__ == '__main__':
    unittest.main()