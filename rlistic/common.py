import os.path # For reading from file
from typing import Callable # For type hinting

# Check if the level-set is correct
def validate_level_set(level_set:list[float]) -> None:
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

# Check if the RLs mapping is correct        
def validate_mapping(mapping:dict) -> None:
    if not isinstance(mapping, dict):
        raise TypeError("Mapping must be a dictionary")
    # Verify the level-set
    validate_level_set(list(mapping.keys()))
    # Check if all objects are of the same type with set comprehension
    if len({type(obj) for obj in mapping.values()}) != 1:
        raise TypeError("All instances must be of the same class")

# Visualize RL in table format
def rl_table(cls_name:str, mapping:dict) -> str:
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

# Fuzzy set {a : 0.8, b : 0.7, etc...} to RL {1: {}, 0.8 : {a}, etc...}
def fuzzy_to_rl(fuzzy_set:dict) -> dict:
    pass

# Obtain fuzzy summary of an RL
def rl_fuzzy_summary(rl:dict) -> dict:
    pass

# Read RL from file
def read_rl_input(input_file: str, process:Callable = None) -> dict:
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