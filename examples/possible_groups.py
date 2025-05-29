import sys

def divisors(n: int) -> list[int]:
    """ Return proper divisors of n (excluding 1 and n). """
    return {str(d) for d in range(2, n) if n % d == 0}

# Read from stdin and split the input by commas
data = sys.stdin.read().strip().split(',')

# Call divisors on the cardinal of the input set
div = divisors(len(data))

# Output the comma-separated divisors to stdout
print(','.join(div))