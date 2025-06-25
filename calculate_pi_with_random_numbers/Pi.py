import math
import random

class Pi:
    ROUND_POINT = 6
    RANDOM_NUMBER_HIGH_RANGE = 10**9
    generated = 0
    actual = 3.141593

    def __init__(self, numberOfRandomNumber = 1000):
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
        difference = round(math.fabs(self.generated - self.actual), self.ROUND_POINT)
        accuracy =  (1 - (math.fabs(self.generated - self.actual) / self.actual))*100

        # printing
        print("Result".center(20, '-'))
        print(f"Generated pi = {self.generated}\n" \
        f"Actual pi = {self.actual}\n" \
        f"Difference = {difference}\n" \
        f"Accuracy = {accuracy:.4}%\n")

    def __swapGcdNumber(self):
        temp = self.a_gcdNumber
        self.a_gcdNumber = self.b_gcdNumber
        self.b_gcdNumber = temp

    def Gcd(self, a: int, b: int) -> int:
        self.a_gcdNumber, self.b_gcdNumber = a, b

        # if a < b
        self.__swapGcdNumber()

        while True:
            if self.a_gcdNumber % self.b_gcdNumber == 0:
                break
            else:
                temp = self.a_gcdNumber % self.b_gcdNumber
                self.a_gcdNumber = self.b_gcdNumber
                self.b_gcdNumber = temp
        return self.b_gcdNumber
    
    def isCoprime(self, a: int, b: int) -> bool:
        return self.Gcd(a, b) == 1
    

