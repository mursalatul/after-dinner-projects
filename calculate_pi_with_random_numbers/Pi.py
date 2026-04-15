import math
import random

class Pi:
    """
    Calculates the value of Pi using the probability that two random numbers are coprime.
    
    The mathematical principle states that the probability of two random integers 
    being coprime is 6/(pi^2).
    """
    ROUND_POINT = 6
    RANDOM_NUMBER_HIGH_RANGE = 10**9
    generated = 0
    actual = 3.141593

    def __init__(self, numberOfRandomNumber = 1000):
        """
        Initializes the Pi calculation by generating random pairs and checking for coprimality.

        Args:
            numberOfRandomNumber (int): The total number of random pairs to test. 
                                        Higher values lead to better accuracy.
        """
        # generate pi with random number
        numberOfCoprime = 0
        for _ in range(numberOfRandomNumber):
            randomNumber1 = random.randint(0, self.RANDOM_NUMBER_HIGH_RANGE)
            randomNumber2 = random.randint(0, self.RANDOM_NUMBER_HIGH_RANGE)
            if self.isCoprime(randomNumber1, randomNumber2):
                numberOfCoprime += 1

        x = numberOfCoprime / numberOfRandomNumber
        self.generated = round(math.sqrt(6 / x), self.ROUND_POINT)

    def showResult(self):
        """
        Calculates the difference and accuracy of the generated Pi vs the actual value 
        and prints the results to the console.
        """
        difference = round(math.fabs(self.generated - self.actual), self.ROUND_POINT)
        accuracy =  (1 - (math.fabs(self.generated - self.actual) / self.actual))*100

        # printing
        print("Result".center(20, '-'))
        print(f"Generated pi = {self.generated}\n" \
        f"Actual pi = {self.actual}\n" \
        f"Difference = {difference}\n" \
        f"Accuracy = {accuracy:.4}%\n")

    def __swapGcdNumber(self):
        """Internal helper to swap current GCD operands."""
        temp = self.a_gcdNumber
        self.a_gcdNumber = self.b_gcdNumber
        self.b_gcdNumber = temp

    def Gcd(self, a: int, b: int) -> int:
        """
        Calculates the Greatest Common Divisor (GCD) of two numbers using the Euclidean algorithm.

        Args:
            a (int): First integer.
            b (int): Second integer.

        Returns:
            int: The Greatest Common Divisor.
        """
        self.a_gcdNumber, self.b_gcdNumber = a, b

        # if a < b, swap them
        if self.a_gcdNumber < self.b_gcdNumber:
            self.__swapGcdNumber()

        while True:
            if self.b_gcdNumber == 0:
                return self.a_gcdNumber
            if self.a_gcdNumber % self.b_gcdNumber == 0:
                break
            else:
                temp = self.a_gcdNumber % self.b_gcdNumber
                self.a_gcdNumber = self.b_gcdNumber
                self.b_gcdNumber = temp
        return self.b_gcdNumber
    
    def isCoprime(self, a: int, b: int) -> bool:
        """
        Determines if two numbers are coprime (GCD is 1).

        Args:
            a (int): First integer.
            b (int): Second integer.

        Returns:
            bool: True if coprime, False otherwise.
        """
        return self.Gcd(a, b) == 1
    

