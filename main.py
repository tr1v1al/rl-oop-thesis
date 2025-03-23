import ast  # For parsing and manipulating Python code as an AST
import os   # For handling file paths and directories

# Template for the RL class as a string; {original_name} will be replaced
RL_CLASS_TEMPLATE = """
class RL{original_name}:
    def __init__(self, map_dict):
        if not isinstance(map_dict, dict):
            raise TypeError('Input must be a dictionary')
        if 1 not in map_dict:
            raise ValueError('Level 1 must be present in every RL')
        for alpha in map_dict:
            if not 0 < alpha <= 1:
                raise ValueError('Levels must be in (0, 1]')
        self.map_dict = {{alpha: deepcopy(obj) for alpha, obj in map_dict.items()}}
    
    def combine_levels(self, other):
        lvls1, lvls2 = list(self.map_dict.keys()), list(other.map_dict.keys())
        i1, i2, levels = 0, 0, []
        while (i1 < len(lvls1) and i2 < len(lvls2)):
            curr1, curr2 = lvls1[i1], lvls2[i2]
            levels.append(curr1 if curr1 >= curr2 else curr2)
            i1 = i1 + 1 if curr1 >= curr2 else i1
            i2 = i2 + 1 if curr2 >= curr1 else i2
        if i1 != len(lvls1): levels.extend(lvls1[i1:])
        if i2 != len(lvls2): levels.extend(lvls2[i2:])
        return levels
"""
# Template for the RL class methods
RL_METHOD_TEMPLATE = """
def {method_name}(self, {other_arg}):
    levels = self.combine_levels({other_arg})
    map_dict, curr1, curr2 = {{}}, self.map_dict[1], {other_arg}.map_dict[1]
    for level in levels:
        curr1 = self.map_dict.get(level, curr1)
        curr2 = {other_arg}.map_dict.get(level, curr2)
        map_dict[level] = curr1.{method_name}(curr2)
    return RL{original_name}(map_dict)
"""

# Template for the RL class __str__ method
STR_METHOD_TEMPLATE = """
def __str__(self):
    return str(self.map_dict)
"""

def rlify_class(node):
    # node is the ClassDef AST node from original class (e.g., Integer)
    original_name = node.name  # Extracts class name
    
    rl_methods = []  # List to store RL-ified method AST nodes
    for item in node.body:  # Loop over original class's methods
        # Check if it’s a special method (starts with __) but not __init__
        if isinstance(item, ast.FunctionDef) and item.name.startswith('__') and item.name != '__init__':
            method_name = item.name  # e.g., '__add__', '__mul__'
            args = item.args.args  # List of arguments (self, other)
            if len(args) > 1:  # Ensure it takes a param beyond self
                other_arg = args[1].arg  # 'other'
                # Create an AST node for the RL-ified method
                rl_method = ast.parse(RL_METHOD_TEMPLATE.format(
                    method_name=method_name,
                    other_arg=other_arg,
                    original_name=original_name
                )).body[0]  # Get the FunctionDef node
                rl_methods.append(rl_method)  # Add to list
    
    # Add __str__ method explicitly
    str_method = ast.parse(STR_METHOD_TEMPLATE).body[0]
    rl_methods.append(str_method)
    
    # Format the template with the original class name
    rl_class_code = RL_CLASS_TEMPLATE.format(original_name=original_name)
    # Parse into AST; body[0] is the ClassDef (no import here)
    rl_class_node = ast.parse(rl_class_code).body[0]
    # Extend RL class with the generated methods
    rl_class_node.body.extend(rl_methods)
    return rl_class_node  # Return the RL class ClassDef node

def transform_file(input_path, output_path):
    # Read input file from input path
    with open(input_path, 'r') as f:
        source = f.read()
    # Parse into an AST (Module node)
    tree = ast.parse(source)
    # Validate: must have exactly one class
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.ClassDef):
        raise ValueError("Input file must contain exactly one class definition")
    # Transform the class into RL version
    rl_class_node = rlify_class(tree.body[0])
    # Add import and unparse to source code
    output_code = f"from copy import deepcopy\n\n{ast.unparse(rl_class_node)}"
    # Write to output file (e.g. rl_integer.py)
    with open(output_path, 'w') as f:
        f.write(output_code)

def main(input_filename):
    # Set directories
    input_dir = "input"
    output_dir = "output"
    # Construct full paths
    input_path = os.path.join(input_dir, input_filename)  # e.g., input/integer.py
    output_filename = f"rl_{input_filename}"  # e.g., rl_integer.py
    output_path = os.path.join(output_dir, output_filename)
    # Create directories if they don’t exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    # Run the transformation
    transform_file(input_path, output_path)
    print(f"Transformed {input_filename} to {output_filename}")

# Entry point: runs if script is executed directly
if __name__ == "__main__":
    import sys
    # Check for command-line argument
    if len(sys.argv) != 2:
        print("Provide the name of the input file in the input directory as follows: python main.py <input_filename>")
        sys.exit(1)
    main(sys.argv[1])  # Pass filename (e.g., integer.py)