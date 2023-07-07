def is_prime(n):
    """
    Returns True if n is prime, False otherwise.
    """
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n%2 == 0 or n%3 == 0:
        return False
    i = 5
    while i*i <= n:
        if n%i == 0 or n%(i+2) == 0:
            return False
        i += 6
    return True

def prime_in_interval(x,y):
    """
    Returns a list of prime numbers in the interval [x,y].
    """
    count = 0
    for i in range(x,y+1):
        if is_prime(i):
            count += 1
    return count