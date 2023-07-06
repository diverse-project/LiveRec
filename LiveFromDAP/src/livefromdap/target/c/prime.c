int is_prime(int x){
    for (int i = 2; i <= x / 2; i++) {
        if (x % i == 0) {
            return 0;
        }
    }
    return 1;
}

int prime_in_interval(int x, int y){
    // Return the number of prime numbers in the interval [x, y]
    int count = 0;
    for (int i = x; i <= y; i++) {
        if (is_prime(i)) {
            count++;
        }
    }
    return count;
}