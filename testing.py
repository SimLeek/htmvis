'''import numpy as np

x = np.arange(20,1,-1)

indices = np.arange(0,10,2)

subtractor = 5

x[indices] -=subtractor

print(x)'''

#from wolfram
#sum_(i=0)^z (x - 1)^i (-i + z + 1) = (x^2 (x - 1)^z - 2 x (x - 1)^z + (x - 1)^z - x z - 2 x + 2 z + 3)/(x - 2)^2
# where z=zeros, x=ones
#next:
# solve for z, q=(sum i=0 to z, ((z-i+1)*(x-1)^i))

import unittest

import math as m
from scipy.special import lambertw
from scipy.special import binom

def min_bits(ones, sparsity):
    return int(m.ceil(ones/sparsity))

def min_zeros( ones, sparsity):
    return min_bits(ones,sparsity)-ones

def all_possibilities(zeros, ones):
    if ones == 1:
        return (zeros + 1)
    result = (zeros+1)*(ones+zeros)*binom(ones+zeros-1, ones-2) / ((ones-1)*ones)

    return result

def find_height_leq(function, height_value):
    power = 0

    while True:



print(find_height_leq(lambda x:min_zeros(x, 0.02), 10000))

def bits_required(ones, max_number):
    if ones <=0:
        raise ValueError("ones cannot be below or equal to 0.")
    if ones == 1:
        #https://www.wolframalpha.com/input/?i=solve+for+z,+q%3D(z+%2B+1)
        num_zeros = max_number - 1
        return num_zeros + ones
    if ones == 2:
        #https://www.wolframalpha.com/input/?i=solve+for+z,+q%3D(((z%2B+1)*(z%2B+2))%2F2)+-+1
        num_zeros = m.ceil((-3+m.sqrt(8*max_number+1))/2.0)
        return num_zeros + ones

    guess = 200
    iteration = 1

    while True:
        if all_possibilities(guess-1, ones)>max_number:
            guess = int(m.ceil(guess - max((guess/(2.0**iteration)),1)))
            #print('+', guess)
        elif all_possibilities(guess, ones)<max_number:
            guess = int(m.floor(guess + max((guess/(2.0**iteration)),1)))
            #print('-', guess)
        else:
            print(cumulative_possibilities(guess, ones, guess),'i',max_number)
            if cumulative_possibilities(guess, ones, guess)==max_number:
                return guess+1
            return guess
        iteration+=1



def possibilities(zeros, ones, zeros_between_ones):
    if ones==1 and zeros_between_ones == 0: #we need to specify that 0^0=1 in this case
        return (zeros +1)
    return (zeros - zeros_between_ones+1)*binom(zeros_between_ones+ones-2, ones-2)


def cumulative_possibilities(zeros, ones, zeros_between_ones):
    x=ones
    z=zeros
    m=zeros_between_ones

    result = -((m + 1) *binom(m + x - 1, x - 2)* (m *(x - 1) - x *(z + 1)))/((x - 1) *x)
    #print('cumulative:',result)

    return result

def find_zeros_between_ones_level(zeros, ones, i):
    if ones == 1:
        return 0
    if ones == 2:
        # https://www.wolframalpha.com/input/?i=solve+for+b,+m%3D-(1%2F2)+(1+%2B+b)+(-2+%2B+b+-+2+z)
        return (m.sqrt(8*i+4*zeros**2 + 12*zeros + 9) + 2*zeros +1)

    # try https://www.wolframalpha.com/input/?i=solve+for+b,++m%3D(x%5E2+(z+%2B+1)+(x+-+1)%5Eb+-+b+(x%5E2+-+3+x+%2B+2)+(x+-+1)%5Eb+%2B+2+z+(x+-+1)%5Eb+-+x+(3+z+(x+-+1)%5Eb+%2B+2+(x+-+1)%5Eb+%2B+z+%2B+2)+%2B+(x+-+1)%5Eb+%2B+2+z+%2B+3)%2F(x+-+2)%5E2
    # ProductLog function doesn't seem to work, but if it did it could get this closer to O(1)
    # Currently, it works in log(n) time

    guess = int(m.floor(zeros/2))

    iteration = 1

    #https://www.wolframalpha.com/input/?session_id=57260e60-c366-44dc-9dd6-ef349bba734d&oauth_token=41faf1a3be074af6c3306305dd6f470f058a87395&oauth_verifier=e8dbdab947&remember_me=true&i=sum+j%3D0,m,+(z-+m%2B1)*(x-1)%5Em

    while True:
        if cumulative_possibilities(zeros, ones, guess-1)>i:
            guess = int(m.ceil(guess - max((zeros/(2.0**iteration)),1)))
            #print('+', guess)
        elif cumulative_possibilities(zeros, ones, guess)<i:
            guess = int(m.floor(guess + max((zeros/(2.0**iteration)),1)))
            #print('-', guess)
        else:
            #print(cumulative_possibilities(zeros, ones, guess),'i',i)
            if cumulative_possibilities(zeros, ones, guess)==i:
                return guess+1
            return guess
        iteration+=1

def find_permutation_number(zeros, ones, zeros_between_ones, overflow):
    perm = m.floor(overflow / (zeros - zeros_between_ones + 1))
    return perm

def find_zeros_before_permutation(zeros, ones, zeros_between_ones, permutation_number,
                                  overflow):
    if (zeros_between_ones%2==0 and permutation_number%2==0) or \
        (zeros_between_ones%2==1 and permutation_number%2==1):
        return int(overflow)
    else:
        #this way, the number moves back and forth, improving locality
        return int((zeros-zeros_between_ones) - overflow)

import operator as op
def choose(n, r):
    r = min(r, n - r)
    if r == 0: return 1
    try:
        numer = reduce(op.mul, xrange(n, n - r, -1))
        denom = reduce(op.mul, xrange(1, r + 1))
    except:
        return 0
    return numer // denom

# put 0s in between 1s, assign 1 slot to each 0. eq: #of slots^#of 0s
# to determine remaining: #of slots left^#of 0s left
# put 0s in between 1s, assign 1 slot to each 0. eq: #of slots^#of 0s
# to determine remaining: #of slots left^#of 0s left
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

def build_number(n_perm_array, zeros_before_perm, zeros_between_ones, zeros):

    out_arr = n_perm_array
    for i in range(zeros_before_perm):
        out_arr.insert(0,0) #prepend 0
    for i in range(zeros - zeros_before_perm - zeros_between_ones):
        out_arr.append(0)

    return out_arr


class TestNeuronIntegers(unittest.TestCase):
    def test_possibilities(self):
        self.assertEqual(possibilities(196, 4, 20), 617160838977)
        print(all_possibilities(196, 4 ))

    def test_cumulative_possibilities(self):
        self.assertEqual(cumulative_possibilities(196, 4, 20), 12960377618517)

    def test_all_possibilities(self):
        self.assertEqual(all_possibilities(196, 4),7378166357663188037188370056549434078589818129260958221515971159419235858369505083177352751123)

    def test_find_zeros_between_ones(self):
        self.assertEqual(find_zeros_between_ones_level(196, 4, 12960377618516), 20)

    def test_find_permutation_number(self):
        self.assertEqual(find_permutation_number(196, 4, 21, 600),3)

    def test_conversion(self):
        for i in range(0,10000):
            a = find_zeros_between_ones_level(196, 4, i)
            #print('a',a)
            overflow = i - cumulative_possibilities(196, 4, a-1)
            #print('overflow', overflow)
            p_num = find_permutation_number(196, 4, a, overflow)
            #print('p_num', p_num)
            zeros_before_perm = find_zeros_before_permutation(196, 4, a, p_num,
                                  overflow%(196 - a + 1))
            #print('zeros_before_perm', zeros_before_perm)

            if a==0:
                the_perm = [1 for x in range(4)]
            else:
                the_perm = nth_perm(p_num, 4-2, a+4-2, clamp=False, wrap=False)
                the_perm.insert(0,1)
                the_perm.append(1)
            #print(the_perm)
            the_number = build_number(the_perm, zeros_before_perm, a, 196)
            print(the_number)




'''if __name__=='__main__':
    unittest.main()'''