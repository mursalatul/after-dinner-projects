# Calculating Pi Using Random Numbers (Monte Carlo Method)

A Python implementation for estimating the value of Archimedes' constant (Pi) using the mathematical properties of coprime numbers.

## Theoretical Background
This project uses the property that the probability of two randomly chosen integers being coprime (having a Greatest Common Divisor of 1) is exactly:

$$P(\text{coprime}) = \frac{6}{\pi^2}$$

By generating a large set of random pairs and determining what fraction of them are coprime, we can estimate $\pi$ using the formula:

$$\pi \approx \sqrt{\frac{6}{P(\text{coprime})}}$$

## Features
- **Custom GCD Implementation:** Uses the Euclidean algorithm to determine divisors.
- **Accuracy Tracking:** Compares the generated result with the standard $\pi \approx 3.141593$.
- **Configurable Precision:** Adjust the number of iterations to see how the estimate converges.

## Prerequisites
- Python 3.x

## How to Run
```bash
python main.py
```

## Configuration
To increase the accuracy, you can pass a larger number of iterations to the `Pi` class in `main.py`:
```python
# In main.py
pi = Pi(numberOfRandomNumber=1000000) # One million iterations
```

## Files
- `Pi.py`: Contains the `Pi` class and the core mathematical logic.
- `main.py`: Entry point for executing the calculation.
