def multiplications(n):
    for i in range (1,n+1):
        for j in range (1,n+1):
            if n==i*j :
                count+=1
            if n==i*j==j*i:
                count=count-1
    return (count)