# Task: Fibonacci Generator
# The Fibonacci series is a sequence where each number is the sum of the
# two preceding numbers, defined by a mathematical recurrence
# relationship.

def fibonacci_generator():
    """
    Generator function for Fibonacci sequence.
    Yields the next number in the Fibonacci sequence indefinitely.
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Print the first 10 Fibonacci numbers
if __name__ == "__main__":
    fib = fibonacci_generator()
    for _ in range(10):

        print(next(fib))
