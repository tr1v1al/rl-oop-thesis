import argparse
import ast
import os
from .common import validate_mapping, rl_table

# Registry for RL classes: maps original class to RL class (e.g., {A: RLA})
RL_REGISTRY = {}

# Methods to ignore during RLification
ignore_methods = [
    '__init__', '__str__', '__repr__', '__getattr__', '__setattr__',
    '__new__', '__class__', '__getattribute__', '__delattr__'
]

class _RLBase:
    """Base class for RL classes, providing shared functionality."""

    # Class atribute that determines to which class A the RLA corresponds
    _instance_class = None

    def __init__(self, mapping: dict):
        """Initialize the RL with a level-to-object mapping."""
        
        # Validate the level-set and the objects to rlify
        validate_mapping(mapping)

        # Ensure that the RLA class can only be instantiated with objects of A
        if not all(isinstance(obj, type(self)._instance_class) for obj in mapping.values()):
            raise TypeError(f"All mapping values must be instances of {type(self)._instance_class.__name__}")
        
        # Save the mapping of levels to objects
        self.__mapping = mapping

    @property
    def mapping(self) -> dict:
        """
        Get the internal RL mapping.

        Returns:
            dict: Mapping of levels to objects.
        """

        return self.__mapping

    def get_level_set(self) -> list[float]:
        """
        Get the level-set of the RL.

        Returns:
            list[float]: Level-set.
        """

        return list(self.mapping.keys())
 
    def get_object(self, level, default=None):
        """
        Get the object at a given level or a default value.

        Args:
            level (float): Level to query.
            default: Value to return if level is not found (default: None).

        Returns:
            object: Object at the level or default value.
        """

        return self.mapping.get(level, default) 

    def __combine_levels(self, *args, **kwargs) -> list[float]:
        """
        Combine levels from this RL and other RLs provided as arguments.

        Args:
            *args: RLs passed as positional arguments.
            **kwargs: RLs passed as keyword arguments.

        Returns:
            list[float]: Combined levels in descending order.
        """

        # Helper function for merging two ordered arrays (descending)
        def combine_levels_2lists(lvls1, lvls2):
            i1, i2, levels = 0, 0, []
            # Merge until reaching the end of an array
            while i1 < len(lvls1) and i2 < len(lvls2):
                curr1, curr2 = lvls1[i1], lvls2[i2]
                levels.append(curr1 if curr1 >= curr2 else curr2)
                i1 = i1 + 1 if curr1 >= curr2 else i1
                i2 = i2 + 1 if curr2 >= curr1 else i2
            # Extend with remaining levels
            if i1 != len(lvls1): levels.extend(lvls1[i1:])
            if i2 != len(lvls2): levels.extend(lvls2[i2:])
            return levels   

        # Levels of self
        levels = self.get_level_set()
        
        # Combine with levels from other RLs
        # Positional RL arguments
        for arg in args:
            other = arg.get_level_set()
            levels = combine_levels_2lists(levels, other)
        
        # Keyword RL arguments
        for kwarg in kwargs.values():
            other = kwarg.get_level_set()
            levels = combine_levels_2lists(levels, other)

        return levels

    def general_method(self, method_name: str, *args, **kwargs):
        """
        Apply a method level-wise across RLs, aggregating the result in an RL.
        Arguments can be RLs or crisp, the latter are extended to other levels.
        The output is an RL or crisp, if the objects on all levels are equal.

        Args:
            method_name (str): Name of the method to apply (e.g., '__add__', 'union').
            *args: Positional arguments, may include RLs or crisp objects.
            **kwargs: Keyword arguments, may include RLs or crisp objects.

        Returns:
            RL or object: Resulting RL or crisp object (if same object on all levels).
        """

        # RLify crisp arguments with list/dict comprehension
        # If an argument is not a child of the base RL class, it is treated as crisp,
        # and rlified. If the object has a corresponding RL class, its RL is instantiated
        # If not, throw an error

        # Positional arguments
        rl_args = []
        for arg in args:
            if not isinstance(arg, _RLBase):
                arg_type = type(arg)
                try:
                    rl_class = RL_REGISTRY[arg_type]
                except KeyError:
                    raise TypeError(f"No RL class defined for {arg_type.__name__}")
                arg = rl_class({1.0: arg})
            rl_args.append(arg)

        # Keyword arguments
        rl_kwargs = {}
        for key, obj in kwargs.items():
            if not isinstance(obj, _RLBase):
                obj_type = type(obj)
                try:
                    rl_class = RL_REGISTRY[obj_type]
                except KeyError:
                    raise TypeError(f"No RL class defined for {obj_type.__name__}")
                obj = rl_class({1.0: obj})
            rl_kwargs[key] = obj

        # Get all levels
        levels = self.__combine_levels(*rl_args, **rl_kwargs)

        # Mapping dictionary for the returned RL
        mapping = {}

        # Objects at current level, used to extend to levels not present in the level set
        # Initialized to level 1. Self, positional and keyword arguments.
        curr_self = self.get_object(level=1)
        curr_args = [rl_arg.get_object(level=1) for rl_arg in rl_args]
        curr_kwargs = {key : rl_kwarg.get_object(level=1) for key, rl_kwarg in rl_kwargs.items()}

        # Perform operations levelwise
        prev = None
        for level in levels:
            # Retrieve objects at the current level. 
            # If level is not present, fall back to previous level
            curr_self = self.get_object(level, curr_self)
            curr_args = [rl_arg.get_object(level, curr) for rl_arg, curr in zip(rl_args, curr_args)]
            curr_kwargs = {
                key : rl_kwarg.get_object(level, curr) 
                for (key, rl_kwarg), curr 
                in zip(rl_kwargs.items(), curr_kwargs.values())
            }
            # Operate with arguments at the current level. Retrieve the method_name method
            # for self and then call it with positional and keyword arguments
            # If an error occurs, it is caught and the message is prepended
            try:
                curr = getattr(curr_self, method_name)(*curr_args, **curr_kwargs)
            except Exception as e:
                raise type(e)(f"Error in {self.__class__.__name__} at level {level}: {e}") from e

            # Add to mapping only if the object is on level 1
            # or not the same as on the previous level
            if level == 1 or curr != prev: mapping[level] = curr
            prev = curr

        # Return crisp object if RL only has one level
        if len(mapping) == 1:
            return mapping[1]
        
        # Get the class of the objects obtained as output 
        result_type = type(mapping[1])

        # If the output is of a class yet to be rlified, return error
        try:
            rl_class = RL_REGISTRY[result_type]
        except KeyError:
            raise TypeError(f"No RL class defined for {result_type.__name__}")
        
        # Return an RL of the corresponding class
        return rl_class(mapping)

    def __str__(self) -> str:
        """
        Get a string representation of the RL as a table.

        Returns:
            str: Table formatted by rl_table showing levels and objects.
        """

        return rl_table(type(self)._instance_class.__name__, self.mapping)

def rlify_class(node: ast.ClassDef) -> tuple[str, str]:
    """
    Generate code for the RL class from a class definition node using AST, copying
    the original class's method signatures and delegating to general_method
    in the body of the RL class's methods.
    
    Args:
        node (ast.ClassDef): node of the original class. 
    Returns:
        str: Code of the RL class.
        str: Name of the original class.
    """
    # Extract the name of the original class
    class_name = node.name
    # List to store the rlified methods of the RL class
    rl_methods = []

    # Iterate over the nodes of the class's body
    for item in node.body:
        # If the node is a method, rlify it
        if isinstance(item, ast.FunctionDef) and item.name not in ignore_methods:
            # Extract the name of the method
            method_name = item.name
            # Extract the method's signature (positional, keyword args, etc.)
            args = item.args

            # Gather the arguments that will be used to call general_method in the 
            # body of the method. We store the arguments we will use in lists
            # The first arg for general_method is the name of the method
            call_args = [ast.Constant(value=method_name)]

            # Positional args, skipping self
            for arg in args.args[1:]:
                call_args.append(ast.Name(id=arg.arg, ctx=ast.Load()))

            # Variable args (*args)
            if args.vararg:
                call_args.append(ast.Starred(
                    value=ast.Name(id=args.vararg.arg, ctx=ast.Load()),
                    ctx=ast.Load()
                ))
            
            # Keyword-only args
            call_keywords = []
            for arg in args.kwonlyargs:
                call_keywords.append(ast.keyword(
                    arg=arg.arg,
                    value=ast.Name(id=arg.arg, ctx=ast.Load())
                ))

            # Variable kwargs (**kwargs)
            if args.kwarg:
                call_keywords.append(ast.keyword(
                    arg=None,
                    value=ast.Name(id=args.kwarg.arg, ctx=ast.Load())
                ))

            # Construct the body of the RL method. It contains a single statement:
            # return self.general_method(method_name, params...)
            method_body = [
                ast.Return(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='self', ctx=ast.Load()),
                            attr='general_method',
                            ctx=ast.Load()
                        ),
                        args=call_args,
                        keywords=call_keywords
                    )
                )
            ]

            # Create method node with original signature and the body we defined
            # The RL method has the same name as the original, same signature,
            # and the body we defined above (which delegates to general_method)
            rl_method = ast.FunctionDef(
                name=method_name,
                args=args,
                body=method_body,
                decorator_list=[],
                returns=None
            )

            # Needed for AST to work
            ast.fix_missing_locations(rl_method)
            # Add the method to the list of RL methods
            rl_methods.append(rl_method)

    # Create RL class node. The class has the same name as the original, 
    # with an 'RL' as prefix. It inherits from the _RLBase class, and contains
    # the RL-methods in its body.
    rl_class = ast.ClassDef(
        name=f"RL{class_name}",
        bases=[ast.Name(id='_RLBase', ctx=ast.Load())],
        keywords=[],
        body=rl_methods,
        decorator_list=[]
    )

    # Set class attribute _instance_class to tie the RLclass to the original
    assign_node = ast.Assign(
        targets=[ast.Name(id='_instance_class', ctx=ast.Store())],
        value=ast.Name(id=class_name, ctx=ast.Load())
    )

    ast.fix_missing_locations(assign_node)
    # Insert the class attribute at the beginning of the RL class's body
    rl_class.body.insert(0, assign_node)
    ast.fix_missing_locations(rl_class)

    # Unparse the resulting class node into string, and return it with the name
    return ast.unparse(rl_class), class_name

def transform_file(input_path: str, output_path: str) -> None:
    """
    Transform classes in input file to RL classes and write to output file.
    
    Args:
        input_path (str): Path to input file with original classes.
        output_path (str): Path to output file where RL classes will be written.
    """

    # Check if exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist")

    # Read input file
    with open(input_path, 'r') as f:
        source = f.read()

    # Attempt to parse code into an AST node
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python code in {input_path}: {e}")

    # Rlify classes
    rl_classes = []
    class_names = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            rl_class_code, class_name = rlify_class(node)
            rl_classes.append(rl_class_code)
            class_names.append(class_name)

    if not rl_classes:
        raise ValueError("Input file must contain at least one class definition")

    # Generate output code, importing _RLBase
    output_code = [
        "from rlistic.static import _RLBase, RL_REGISTRY",
        ""
    ]

    # Include original classes into the output
    original_classes = [ast.unparse(node) for node in tree.body if isinstance(node, ast.ClassDef)]
    output_code.extend(original_classes)
    output_code.append("")

    # Include RL classes
    output_code.extend(rl_classes)

    # Populate RL_REGISTRY, mapping original classes to their RL class
    output_code.append("")
    for class_name in class_names:
        output_code.append(f"RL_REGISTRY[{class_name}] = RL{class_name}")

    # Write to output
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(output_code))  

if __name__ == "__main__":
    # Parse to extract arguments (input/output file paths)
    parser = argparse.ArgumentParser(description="Statically RLify Python classes.")
    parser.add_argument("-i", "--input", required=True, help="Input file with class definitions")
    parser.add_argument("-o", "--output", required=True, help="Output file for RL classes")
    args = parser.parse_args()

    # Rlify input, writing to output
    try:
        transform_file(args.input, args.output)
        print(f"Completed RLification: {args.input} -> {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)