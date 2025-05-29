import sys

def sum_squares(start, end):
    """Compute sum of squares for a range of integers."""
    return sum(i * i for i in range(start, end))

data = sys.stdin.read().strip().split()
data = [int(el) for el in data]
data = data[0]
print(f"Processed: {sum_squares(0,data)}")