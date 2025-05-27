# tests/test_rlprogram.py
import unittest
import os
import shlex
import tempfile
from pathlib import Path  # Add pathlib for cross-platform paths
from rlistic.rlprogram import rlify_program, run_program
from rlistic.common import rl_table

class TestRLProgram(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

        # Create mock executable Python script
        self.mock_script = os.path.join(self.temp_path, "mock_program.py")
        with open(self.mock_script, "w") as f:
            f.write('''import sys
data = sys.stdin.read().strip()
print(f"Processed: {data}")
''')

        # Create valid input file
        self.input_file = os.path.join(self.temp_path, "inputs.txt")
        with open(self.input_file, "w") as f:
            f.write("1 0.8\ninput1\ninput2\n")

        # Create invalid level input file
        self.invalid_level_file = os.path.join(self.temp_path, "invalid_levels.txt")
        with open(self.invalid_level_file, "w") as f:
            f.write("1 1.1\ninput1\n")

        # Create mismatched input file
        self.mismatch_file = os.path.join(self.temp_path, "mismatch.txt")
        with open(self.mismatch_file, "w") as f:
            f.write("1 0.8\ninput1\n")

    def tearDown(self):
        # Cleanup handled by TemporaryDirectory
        self.temp_dir.cleanup()

    def test_run_program(self):
        """Test run_program executes command and captures output."""
        # Normalize path for Windows
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]  # Avoid shlex.split for simplicity
        output = run_program(command, "test_input")
        self.assertEqual(output, "Processed: test_input")

    def test_rlify_program_sequential(self):
        """Test rlify_program with sequential execution (nproc=1)."""
        # Normalize path
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        result = rlify_program(command, self.input_file, nproc=1)
        expected = {1.0: "Processed: input1", 0.8: "Processed: input2"}
        self.assertEqual(result, expected)
        table = rl_table("Program", result)
        self.assertIn("RL-Program", table)
        self.assertIn("1.0", table)
        self.assertIn("Processed: input2", table)

    def test_rlify_program_multiprocessing(self):
        """Test rlify_program with multiprocessing (nproc=-1)."""
        # Normalize path
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        result = rlify_program(command, self.input_file, nproc=-1)
        expected = {1.0: "Processed: input1", 0.8: "Processed: input2"}
        self.assertEqual(result, expected)

    def test_invalid_input_file(self):
        """Test rlify_program with non-existent input file."""
        # Normalize path for consistency
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        with self.assertRaises(ValueError) as cm:
            rlify_program(command, os.path.join(self.temp_path, "nonexistent.txt"))
        self.assertEqual(str(cm.exception), "Input file not found: " + os.path.join(self.temp_path, "nonexistent.txt"))

    def test_invalid_levels(self):
        """Test rlify_program with invalid levels."""
        # Normalize path
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        with self.assertRaises(ValueError) as cm:
            rlify_program(command, self.invalid_level_file)
        self.assertIn("Levels must be in (0,1]", str(cm.exception))

    def test_mismatched_inputs(self):
        """Test rlify_program with mismatched input count."""
        # Normalize path
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        with self.assertRaises(ValueError) as cm:
            rlify_program(command, self.mismatch_file)
        self.assertIn("Input file must have 2 input lines, got 1", str(cm.exception))

if __name__ == "__main__":
    unittest.main()