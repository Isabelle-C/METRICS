#!/usr/bin/env python3


class Fibonacci:
    """Fibonacci sequence methods."""

    def __init__(self):
        pass

    @staticmethod
    def calculate(n):
        """Calculate the n-th Fibonacci number.

        An extended description of Fibonacci numbers can go here.

        Parameters
        ----------
        n : int
            Number of Fibonacci sequence to calculate.

        Returns
        -------
        int
            Value of n-th Fibonacci number.
        """

        num_a, num_b = 0, 1

        for _ in range(int(n)):
            num_a, num_b = num_b, num_a + num_b

        return num_a
