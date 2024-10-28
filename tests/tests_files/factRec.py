def fact(n):
    if n <= 1:
        return 1
    prec = fact(n-1)
    return n * prec
