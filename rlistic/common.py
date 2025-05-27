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
        raise ValueError("Levels must be in (0, 1]")
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