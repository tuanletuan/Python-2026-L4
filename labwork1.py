import math

# 1. Calculate Area of a Circle
def circle_area():
    r = float(input("Enter circle radius? "))
    area = 3.14 * (r ** 2)
    print(f"Circle area = {area}")

# 2. Convert Celsius to Fahrenheit
def celsius_to_fahrenheit():
    c = float(input("Enter the temperature in Celsius? "))
    f = (c * 9/5) + 32
    print(f"{c} (C) = {f} (F)")

# 3. Check for Prime Number
def is_prime_number():
    n = int(input("Enter a number? "))
    is_prime = True
    if n <= 1:
        is_prime = False
    else:
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                is_prime = False
                break
    
    if is_prime:
        print(f"{n} is a prime number")
    else:
        print(f"{n} is a NOT prime number")

# 4. Check for Perfect Number
def is_perfect_number():
    n = int(input("Enter a number? "))
    if n <= 1:
        print(f"{n} is a NOT perfect number")
        return
    
    divisors_sum = 0
    for i in range(1, (n // 2) + 1):
        if n % i == 0:
            divisors_sum += i
            
    if divisors_sum == n:
        print(f"{n} is a perfect number")
    else:
        print(f"{n} is a NOT perfect number")

# 5. Favorite Color Index
def favorite_color():
    color_list = ['White', 'Blue', 'Black', 'Red', 'Yellow', 'Green']
    color = input("What is your favorite color? ")
    
    if color in color_list:
        idx = color_list.index(color)
        print(f"Your color is at index {idx} in my list")
    else:
        print("Sorry, I could not find your color")

# 6. Sequence Generation using range()
def print_ranges():
    print("Sequence\n")
    print("range1 |", ", ".join(map(str, list(range(7)))))
    print("range2 |", ", ".join(map(str, list(range(1, 13, 3)))))
    print("range3 |", ", ".join(map(str, list(range(5, 0, -1)))))
    print("range4 |", ", ".join(map(str, list(range(6, -3, -2)))))

# 7. Remove Dollar Sign
def remove_dollar_sign(s):
    return s.replace("$", "")

# 8. Extract Even Numbers
def extract_even(l):
    return [x for x in l if x % 2 == 0]

# 9. Factorial
def calculate_factorial(n):
    if n < 0:
        return None
    fact = 1
    for i in range(1, n + 1):
        fact *= i
    return fact

# 10. Get all divisors
def get_divisors(n):
    divisors = []
    for i in range(1, n + 1):
        if n % i == 0:
            divisors.append(i)
    return divisors

# 11. Distance between two points
def calculate_distance():
    print("Enter coordinates for Point 1:")
    x1 = float(input("x1: "))
    y1 = float(input("y1: "))
    print("Enter coordinates for Point 2:")
    x2 = float(input("x2: "))
    y2 = float(input("y2: "))
    
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    print(f"The distance between the two points is: {dist}")

# 12. Print Pattern m x n
def print_pattern(m, n):
    for _ in range(m):
        print("* " * n)


if __name__ == "__main__":
    circle_area()
    celsius_to_fahrenheit()
    is_prime_number()
    is_perfect_number()
    favorite_color()
    print_ranges()
    
    print(remove_dollar_sign("$100 is my $budget"))
    print(extract_even([1, 4, 5, -1, 10]))
    print(calculate_factorial(5))
    print(get_divisors(28))
    
    calculate_distance()
    print_pattern(5, 5)