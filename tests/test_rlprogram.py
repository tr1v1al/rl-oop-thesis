import unittest
import os
import tempfile
from pathlib import Path
from rlistic.rlprogram import rlify_program, run_program
from rlistic.common import rl_table, rl_input

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

        # Create mock executable Python script with same output
        self.same_script = os.path.join(self.temp_path, "same_program.py")
        with open(self.same_script, "w") as f:
            f.write('''import sys
data = sys.stdin.read().strip()
print(f"Processed: same_output")
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
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        output = run_program(command, "test_input")
        self.assertEqual(output, "Processed: test_input")

    def test_rlify_program_sequential(self):
        """Test rlify_program with sequential execution (nproc=1)."""
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        input_rl = rl_input(self.input_file)
        result = rlify_program(command, input_rl, nproc=1)
        expected = {1.0: "Processed: input1", 0.8: "Processed: input2"}
        self.assertEqual(result, expected)
        table = rl_table("Program", result)
        self.assertIn("RL-Program", table)
        self.assertIn("1.0", table)
        self.assertIn("Processed: input2", table)

    def test_rlify_program_multiprocessing(self):
        """Test rlify_program with multiprocessing (nproc=-1)."""
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        input_rl = rl_input(self.input_file)
        result = rlify_program(command, input_rl, nproc=-1)
        expected = {1.0: "Processed: input1", 0.8: "Processed: input2"}
        self.assertEqual(result, expected)

    def test_invalid_input_file(self):
        """Test rlify_program with non-existent input file."""
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        with self.assertRaises(ValueError) as cm:
            rl_input(os.path.join(self.temp_path, "nonexistent.txt"))
        self.assertEqual(str(cm.exception), "Input file not found: " + os.path.join(self.temp_path, "nonexistent.txt"))

    def test_invalid_levels(self):
        """Test rlify_program with invalid levels."""
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        with self.assertRaises(ValueError) as cm:
            input_rl = rl_input(self.invalid_level_file)
            rlify_program(command, input_rl)
        self.assertIn("Levels must be in (0,1]", str(cm.exception))

    def test_mismatched_inputs(self):
        """Test rlify_program with mismatched input count."""
        mock_script_path = str(Path(self.mock_script).resolve())
        command = ["python", mock_script_path]
        with self.assertRaises(ValueError) as cm:
            input_rl = rl_input(self.mismatch_file)
            rlify_program(command, input_rl)
        self.assertIn("Input file must have 2 input lines, got 1", str(cm.exception))

    def test_squash_crisp(self):
        """Test rlify_program with multiprocessing (nproc=-1)."""
        same_script_path = str(Path(self.same_script).resolve())
        command = ["python", same_script_path]
        input_rl = rl_input(self.input_file)
        result = rlify_program(command, input_rl, nproc=-1)
        expected = "Processed: same_output"
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()