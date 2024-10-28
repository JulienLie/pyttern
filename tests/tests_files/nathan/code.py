def approx_pi(i):        # NE PAS EFFACER CETTE LIGNE
    """
    @pre:   i est un entier tel que i >= 0
    @post:  retourne une estimation de pi en sommant
            les i + 1 premiers termes de la série de Gregory-Leibniz
    """
    numéro = 0
    i = i
    for a in range(0, i + 1):
        n = -4 * (((-1) ^ a) / ((2 * a) + 1))
        a = a + 1
    return numéro
