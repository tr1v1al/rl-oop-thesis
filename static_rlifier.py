import ast  # For parsing and manipulating Python code as an AST (Abstract Syntax Tree)
import os   # For handling file paths and directories

# Template for the RL class
RL_CLASS_TEMPLATE = """
class RL{class_name}:
    def __init__(self, map_dict):
        if not isinstance(map_dict, dict): raise TypeError('Input must be a dictionary')
        if 1 not in map_dict: raise ValueError('Level 1 must be present in every RL')
        prev = 1
        for alpha in map_dict:
            if prev < alpha: raise ValueError('Levels must be in descending order')
            prev = alpha
            if not 0 < alpha <= 1: raise ValueError('Levels must be in (0, 1]')
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
# Template for the RL class binary methods
RL_METHOD_TEMPLATE = """
def {method_name}(self, {other_arg}):
    levels = self.combine_levels({other_arg})
    map_dict, curr1, curr2 = {{}}, self.map_dict[1], {other_arg}.map_dict[1]
    for level in levels:
        curr1 = self.map_dict.get(level, curr1)
        curr2 = {other_arg}.map_dict.get(level, curr2)
        map_dict[level] = curr1.{method_name}(curr2)
    return RL{class_name}(map_dict)
"""

# Template for the RL class unary methods
UNARY_METHOD_TEMPLATE = """
def {method_name}(self):
    map_dict = {{level: obj.{method_name}() for level, obj in self.map_dict.items()}}
    return RL{class_name}(map_dict)
"""

# Template for the RL class __str__ method
STR_METHOD_TEMPLATE = """
def __str__(self):
    return str(self.map_dict)
"""

# Methods in the original class to ignore
IGNORE_METHODS = ['__init__', '__str__', '__repr__', '__getattr__', '__setattr__']

# Function that given a class node returns an RLified class node
def rlify_class(node):
    class_name = node.name  # Extract class name
    # Transform each method in the class
    rl_methods = []
    for item in node.body:
        # Check if it’s a method and not in the ignore list
        if isinstance(item, ast.FunctionDef) and item.name not in IGNORE_METHODS:
            method_name = item.name # Extract method name
            # item.args is the node, item.args.args is the list of arguments
            args = item.args.args
            if len(args) == 2 :  # Binary operation (self, other)
                other_arg = args[1].arg  # Extract parameter name
                # Code for the RL method
                rl_method_code = RL_METHOD_TEMPLATE.format(
                    method_name=method_name,
                    other_arg=other_arg,
                    class_name=class_name
                )
                # Create the RL method node and add it to the list
                rl_methods.append(ast.parse(rl_method_code).body[0])
            elif len(args) == 1:  # Unary operation (self)
                rl_method_code = UNARY_METHOD_TEMPLATE.format(
                    method_name=method_name,
                    class_name=class_name
                )
                rl_methods.append(ast.parse(rl_method_code).body[0])
    
    # Add __str__ method explicitly
    str_method = ast.parse(STR_METHOD_TEMPLATE).body[0]
    rl_methods.append(str_method)
    
    # Format the template with the original class name
    rl_class_code = RL_CLASS_TEMPLATE.format(class_name=class_name)
    # Create class node
    rl_class_node = ast.parse(rl_class_code).body[0]
    # Extend RL class with the generated methods
    rl_class_node.body.extend(rl_methods)
    return rl_class_node  # Return the RL class ClassDef node

# Function for transforming classes in an input file into RL classes
# Params: paths to input/output files
def transform_file(input_path, output_path):
    # Read input file
    with open(input_path, 'r') as f:
        source = f.read()
    # Parse into an AST
    tree = ast.parse(source)
    # Transform each class node (ClassDef)
    rl_classes = [rlify_class(node) for node in tree.body if isinstance(node, ast.ClassDef)]
    # Error if there are no classes in the input file
    if not rl_classes:
        raise ValueError("Input file must contain at least one class.")
    # Add deepcopy at the beginning, then join the code for all the RL classes
    output_code = "from copy import deepcopy\n\n" + "\n\n".join(ast.unparse(cls) for cls in rl_classes)
    # Write to output file
    with open(output_path, 'w') as f:
        f.write(output_code)

# Main function for running this script directly
def main(input_filename):
    # Output file has the name of the input file and rl_ as prefix
    output_filename = f"rl_{input_filename}"
    # Default input/output directories
    input_dir, output_dir = "input", "output"
    # Paths to input and output files
    input_path = os.path.join(input_dir, input_filename)
    output_path = os.path.join(output_dir, output_filename)
    # Transform
    transform_file(input_path, output_path)
    print(f"Transformed {input_filename} to {output_filename}")

# Running this script directly
if __name__ == "__main__":
    import sys
    # Error handling
    if len(sys.argv) != 2:
        print("Correct format: python static_rlifier.py <input_filename>\nInput file must be in input directory")
        sys.exit(1)
    main(sys.argv[1])  # Call main function on the input file