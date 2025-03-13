# converter from int32 to 2 int16
def int32_to_2int16(n):
    n16=[]
    n16.append((n>>16) & 0xFFFF)
    n16.append(n & 0xFFFF)     
    return n16