import os.path # For reading from file
from typing import Callable # For type hinting

# Check if the level-set is correct
def validate_level_set(level_set:list[float]) -> None:
    """
    Validate a level-set of an RL.

    Args:
        level_set (list[float]): List of levels of the RL.

    Raises:
        TypeError: If level_set is not a list or contains non-numeric values.
        ValueError: If level_set is empty, lacks 1, has levels outside (0,1], or is not in descending order.
    """

    if not isinstance(level_set, list):
        raise TypeError("Level-set must be a list")
    if not level_set:
        raise ValueError("Level-set cannot be empty")
    if 1 not in level_set:
        raise ValueError("Level 1 must be present in every RL")
    if not all(isinstance(alpha, (float, int)) for alpha in level_set):
        raise TypeError("Levels must be real numbers")
    if not all(0 < alpha <= 1 for alpha in level_set):
        raise ValueError("Levels must be in (0,1]")
    if level_set != sorted(level_set, reverse=True):
        raise ValueError("Levels must be in descending order")
     
def validate_mapping(mapping:dict) -> None:
    """
    Validate an RLs dictionary mapping of levels to objects.

    Args:
        mapping (dict): Dictionary mapping levels to objects.

    Raises:
        TypeError: If mapping is not a dict or objects are not of the same type.
        ValueError: If the level-set (keys) is invalid per validate_level_set.
    """

    if not isinstance(mapping, dict):
        raise TypeError("Mapping must be a dictionary")
    # Verify the level-set
    validate_level_set(list(mapping.keys()))
    # Check if all objects are of the same type with set comprehension
    if len({type(obj) for obj in mapping.values()}) != 1:
        raise TypeError("All instances must be of the same class")

def rl_table(cls_name:str, mapping:dict) -> str:
    """
    Generate a table representation of an RL.

    Args:
        cls_name (str): Name of the class rlified by the RL.
        mapping (dict): Dictionary mapping levels to objects.

    Returns:
        str: Formatted table string with levels and objects.
    """

    # Compute max width for level column (including header)
    level_width = max(len(str(level)) for level in mapping) + 2
    level_width = max(level_width, len("Level"))
    # Compute max width for object column
    obj_width = max(len(str(obj)) for obj in mapping.values()) + 2
    obj_width = max(obj_width, len("Object"))
    # Build table
    lines = []
    lines.append(f"RL-{cls_name}")
    lines.append(f"{'Level':<{level_width}} | {'Object':<{obj_width}}")
    lines.append("-" * level_width + "-+-" + "-" * obj_width)
    for level, obj in mapping.items():
        lines.append(f"{level:<{level_width}} | {str(obj):<{obj_width}}")
    return "\n".join(lines)

# Read RL from file
def read_rl_input(input_file: str, process:Callable = None) -> dict:
    """
    Read an RL from an input file, optionally process inputs with given function.
    
    Args:
        input_file (str): Path to file with levels (space-separated) on first line, inputs on rest.
        process (Callable, optional): Function that processes the input into the desired format.

    Returns:
        dict: Dictionary with the input RL.
    
    Raises:
        ValueError: If file not found, empty, has invalid levels, or wrong number of inputs.    
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
    
    # Process inputs if processing function is given
    if process is not None:
        inputs = [process(inp) for inp in inputs]

    # Return RL as a dict
    return dict(zip(levels,inputs))

def fuzzy_to_rl(fuzzy_set:dict) -> dict:
    """
    Convert a fuzzy set to an RL-set using alpha-cuts.

    Args:
        fuzzy_set (dict): Dictionary mapping elements to membership degrees.

    Returns:
        dict: Dictionary mapping levels to alpha-cuts.
    """

    # Calculate the levelset Lambda as the union of the degrees with 1 and without 0
    levelset = sorted(set(fuzzy_set.values()).union({1}).difference({0}), reverse=True)

    # Calculate the RL as a mapping of levels to alpha-cuts of the fuzzy set
    rl = {
        alpha : {elem for elem, deg in fuzzy_set.items() if deg >= alpha} 
        for alpha in levelset
    }
    return rl

def rl_fuzzy_summary(rl:dict) -> dict:
    """
    Compute a fuzzy summary of an RL, mapping elements to membership degrees.

    Args:
        rl (dict): Dictionary of an RL mapping levels to sets of elements (crisp realizations).

    Returns:
        dict: Fuzzy set representing the fuzzy summary of the RL as a sorted dictionary 
        mapping elements to membership degrees, descending by degree, then element.

    Raises:
        TypeError: If rl's keys are not a valid level-set per validate_level_set.
        ValueError: If level-set is invalid.
    """

    # Get all the elements as union of all the crisp realizations
    elements = set().union(*rl.values())

    # Validate the level-set
    levels = list(rl.keys())
    validate_level_set(levels)

    # Calculate the probability distribution w(alpha_i) = alpha_i - alpha_{i+1}
    levels = levels + [0]
    w = {
        levels[ind] : levels[ind] - levels[ind+1]
        for ind in range(len(levels)-1)
    }

    # For each element, calculate its presence in the RL
    summary = {
        el : sum(w[alpha] for alpha, rho_alpha in rl.items() if el in rho_alpha) 
        for el in elements
    }
    
    # Sort by degree descending, then by element for ties
    return dict(sorted(summary.items(), key=lambda x: (-x[1], x[0])))