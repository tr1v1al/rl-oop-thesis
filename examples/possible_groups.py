import sys

def group_sizes(students: set) -> set[int]:
    """ Return the proper divisors of the scardinality of students """
    n = len(students)
    return {str(d) for d in range(2, n) if n % d == 0}

# Read from stdin and split the input by commas
students = set(sys.stdin.read().strip().split(','))

# Calculate the possible group sizes for students
gs = group_sizes(students)

# Output the comma-separated divisors to stdout
print(','.join(gs))