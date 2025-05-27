import subprocess
import os.path
import shlex
import sys
import argparse
import multiprocessing
import time
from rlistic.common import validate_level_set, rl_table

def run_program(command: list[str], inp: str) -> str:
    """
    Run a program with input, return output
    
    Args:
        command (list[str]): Command list (e.g., ['python', 'program.py']).
        inp (str): Input to the program.

    Returns:
        output (str): Output captured from the executed program.
    """
    try:
        # Execute program with input while capturing output
        result = subprocess.run(
            command,
            input=inp,
            capture_output=True,
            text=True,
            check=True
        )
        # Return output or if empty, "None"
        return result.stdout.strip() or "None"
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Program execution failed: {e.stderr}")

def rlify_program(command: list[str], input_file: str, nproc: int = -1) -> dict:
    """
    Run a program for each level of the RL, aggregate the output in a table representing the RL.
    
    Args:
        command (list[str]): Command list (e.g., ['python', 'program.py']).
        input_file (str): Path to file with levels (space-separated) on first line, inputs on rest.
        nproc (int): Number of processes (-1: all CPUs, 1: sequential, >1: specific count).

    Returns:
        output (dict): Dictionary with the output RL.
    """
    # Validate input file existence
    if not os.path.isfile(input_file):
        raise ValueError(f"Input file not found: {input_file}")
    
    # Read input from input file, skip empty lines and strip input
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if len(lines) < 1:
        raise ValueError("Input file is empty")
    
    # Parse space-separated levels from first line
    try:
        levels = [float(x) for x in lines[0].split()]
    except ValueError:
        raise ValueError("Levels must be space-separated floats (e.g., '1 0.8')")
    
    # Validate level set
    validate_level_set(levels)
    
    # Get inputs from remaining lines
    inputs = lines[1:]
    if len(inputs) != len(levels):
        raise ValueError(f"Input file must have {len(levels)} input lines, got {len(inputs)}")
    
    # Execute sequentially or with multiprocessing depending on nproc
    if nproc == 0 or nproc < -1:
        raise ValueError(f"Number of processes must be -1 (all CPUs) or >= 1")
    
    results = []
    if nproc == 1:
        # Sequential execution
        for inp in inputs:
            result = run_program(command, inp)
            results.append(result)
    else:
        # Multiprocessing execution
        num_cpus = multiprocessing.cpu_count()
        nproc = num_cpus if nproc == -1 else min(nproc, num_cpus)
        with multiprocessing.Pool(processes=nproc) as pool:
            results = pool.starmap(run_program, [(command, inp) for inp in inputs])
    
    # Zip levels and output into a dictionary
    mapping = dict(zip(levels, results))
    
    return mapping

if __name__ == "__main__":
    # Set up argument parser with short and long flags
    parser = argparse.ArgumentParser(description="Run a command for each level with inputs from a file.")
    parser.add_argument("-i", "--input", required=True, help="Path to input file (space-separated levels on first line, inputs on rest)")
    parser.add_argument("-c", "--command", required=True, help="Command to execute (e.g., 'python program.py')")
    parser.add_argument("-n", "--nproc", type=int, default=-1, help="Number of processes (-1: all CPUs, 1: sequential, >1: specific count)")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Split command string into list
        command_list = shlex.split(args.command)
        # Call rlify_program and get output
        start_time = time.time()  # Start timing
        output=rlify_program(command_list, args.input, args.nproc)
        end_time = time.time()  # End timing
        # Print table with the output RL
        print(rl_table("Program", output))
        print(f"Execution time: {end_time - start_time:.3f} seconds")  # Print elapsed time
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)