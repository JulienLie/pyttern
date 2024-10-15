def approx_pi(n):
    x = 0
    for i in range(0, n+1):
        x = ((-1)**i)/(2*i+1) + x
    x *= 4
    return x
