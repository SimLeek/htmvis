
# from here: http://stackoverflow.com/a/4941932/782170
import operator as op
def choose(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    try:
        numer = reduce(op.mul, xrange(n, n-r, -1))
        denom = reduce(op.mul, xrange(1, r+1))
    except:
        return 0
    return numer//denom

def nth_perm(n, on_bits, total_bits, clamp=False, wrap=False):
    #http://math.stackexchange.com/a/1072064/324663
    assert(not (clamp and wrap))
    if n >= choose(total_bits,on_bits):
        if clamp:
            n = choose(total_bits,on_bits)-1
        elif wrap:
            n = n%choose(total_bits,on_bits)
        else:
            raise IndexError(str(n)+' is larger than max number '+str(choose(total_bits,on_bits)))
    if n <0:
        if clamp:
            n = 0
        elif wrap:
            n = n%choose(total_bits,on_bits)
        else:
            raise IndexError(str(n)+' is smaller than min number '+str(0))

    arr=[]
    for i in range(total_bits):
        if on_bits==0:
            while len(arr)< total_bits:
                arr.append(0)
            break

        if choose(total_bits-(i+1), on_bits) <= n:
            arr.append(1)
            n-=choose(total_bits-(i+1), on_bits)
            on_bits -= 1
        else:
            arr.append(0)


    return arr


if __name__ == '__main__':

    print(nth_perm(256, 4,64))