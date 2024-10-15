def multiplications(n):
    """
    pre:  n est un nombre entier positif
    post: Retourne le nombre de décompositions a,b distinctes
          telles que n == a*b == b*a
    """
    # A COMPLETER #
    print(True)
    b=n
    a=1
    c=0
    d = b[0]
    e = (1,2,3)
    f = 1 + 2 + 3 + 4

    if a or b or a and c: print("ok")
    elif not a and (not c or b):
        print("maybe")
    elif a > c != b:
        print("MMmmh")
    else:
        print("no")

    while a*b==n:
        c=a*(b/a)
        a+=1
    return c
