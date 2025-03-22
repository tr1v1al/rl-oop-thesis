# Example integer class for testing
class Integer:
    # Initialized from an integer
    def __init__(self, val):
        self.val = val
    # Addition method
    def __add__(self, other):
        return Integer(self.val + other.val)
    # Multiplication method
    def __mul__(self, other):
        return Integer(self.val * other.val)
    # For debugging
    def __repr__(self):
        return f"Integer({self.val})"
    # For human readability
    def __str__(self):
        return str(self.val)