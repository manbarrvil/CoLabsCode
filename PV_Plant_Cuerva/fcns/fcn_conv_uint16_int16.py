# converter from uint16 to int16
def toSigned16(n,bit):
    mask = (2**bit) - 1
    if n & (1 << (bit - 1)):
        return n | ~mask
    else: 
        return n & mask