import subprocess
import shlex
import sys
import argparse
import multiprocessing
import time
from .common import rl_table, rl_input

def run_program(command: list[str], inp: str) -> str:
    """
    Run a program with input, return output
    
    Args:
        command (list[str]): Command list (e.g., ['python', 'program.py']).
        inp (str): Input to the program.

    Returns:
        str: Output captured from the executed program.
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

def rlify_program(command: list[str], input_rl: dict, nproc: int = -1) -> dict:
    """
    Run a program for each level of the RL, aggregate the output in a dictionary representing the RL.
    
    Args:
        command (list[str]): Command list (e.g., ['python', 'program.py']).
        input_rl (dict): Input RL as a dictionary mapping levels to input strings.
        nproc (int): Number of processes (-1: all CPUs, 1: sequential, >1: specific count).

    Returns:
        dict or object: Dictionary with the output RL.
    """
    
    # Execute sequentially or with multiprocessing depending on nproc
    if nproc == 0 or nproc < -1:
        raise ValueError(f"Number of processes must be -1 (all CPUs) or >= 1")
    # Get levels and inputs
    levels, inputs = list(input_rl.keys()), input_rl.values()
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
    
    # Zip levels and output into a mapping dictionary, squashing results
    prev, mapping = None, {}
    for level, result in zip(levels, results):
        if level == 1 or result != prev:
            mapping[level] = result
        prev = result
    
    # Return RL or crisp object if there is only 1 level
    return mapping if len(mapping) > 1 else mapping[1]

# Run with python -m rlistic.rlprogram
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
        # Read input
        rl_input = rl_input(args.input)
        # Call rlify_program, get the output and measure the time
        start_time = time.time()  # Start timing
        output = rlify_program(command_list, rl_input, args.nproc)
        end_time = time.time()  # End timing
        # Print table with the output RL, or the object if crisp
        if isinstance(output, dict):
            print(rl_table("Program", output))
        else:
            print("Crisp output:\n", output)
        print(f"Execution time: {end_time - start_time:.3f} seconds")  # Print elapsed time
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)