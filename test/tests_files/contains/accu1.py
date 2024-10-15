def pi(n):
    x = 0
    for i in range(0, n+1):
        x = x + ((-1)**i)/(2*i+1)
    return 4*x
