def approx_pi(i):        # NE PAS EFFACER CETTE LIGNE
    i = 18
    """
    @pre:   i est un entier tel que i >= 0
    @post:  retourne une estimation de pi en sommant
            les i + 1 premiers termes de la série de Gregory-Leibniz
    """
    if i == 0:
        return 4
    pi = 0
    for j in range(i+1) :
        pi += (((-1)**i) / ((2*i)+1))
        return(4*pi)