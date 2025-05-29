# Example integer class for testing
class Integer:
    # Initialized from an integer
    def __init__(self, val):
        self.val = val
    # Power of 2 function
    def pow2(self):
        return Integer(self.val**2)
    # Exponentiation function
    def exp(self, e):
        return Integer(self.val**e)
    # Addition method
    def __add__(self, other):
        return Integer(self.val + other.val)
    # Multiplication method
    def __mul__(self, other):
        return Integer(self.val * other.val)
    # Negation method
    def __neg__(self):
        return Integer(-self.val)
    # For debugging
    def __repr__(self):
        return f"Integer({self.val})"
    # For human readability
    def __str__(self):
        return str(self.val)