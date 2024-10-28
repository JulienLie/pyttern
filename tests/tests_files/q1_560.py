def facteurs(n):
    """
    Pre:  n est un entier strictement positif
    Post: retourne un entier représentant le nombre de facteurs premiers de n
    """
    if n == 1:
        return 0
    else:
        p = 0
        for i in range(2, n):
            for j in range(2, i):
                if i % j == 0:
                    pass
                else:
                    i = p
            return p
        sum = 0
        if n % p == 0:
            sum += 1
            return sum
        else:
            sum += 1
            n = n / p
    return sum
