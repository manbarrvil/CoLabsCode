# converter from int16 to uint16
def toUnsigned16(n,bit):
    if (n>=0 and n<(2**(bit-1))):
        n_uns=n
    elif (n<0 and n>-2**(bit-1)):
        n_uns=n+2**bit
    elif (n>(2**(bit-1))):
        n_uns = (2**(bit-1))-1
    elif (n<-(2**(bit-1))):
        n_uns = (2**(bit-1))
    return n_uns