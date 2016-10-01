# Python hash signature library (quantum resistant)
#
# creates merkle trees for the MSS incorporating either lamport or winternitz OTS.

# creates winternitz OTS key pairs, signs and verifies a winternitz one time signature. 
# creates lamport-diffie OTS key pairs, signs and verifies a lamport one time signature.
#
# todo: full implementation of Winternitz+, IETF Hash-Based Signatures draft-mcgrew-hash-sigs-02 LDWM scheme,
# GMSS and XMSS.


__author__ = 'pete'
from bitcoin import sha256
from bitcoin import random_key
from binascii import unhexlify
import time



def numlist(array):
    for a,b in enumerate(array):
        print a,b
    return

def random_wkey(w=8):      #create random W-OTS keypair
    # Use F = SHA256/SHA512 and G = SHA256/512

    if w > 16:
        w = 16      #too many hash computations to make this sensible.  16 = 3.75s, 8 = 0.01s 1024 bytes..

    priv = []
    pub = []

    start_time = time.time()

    for x in range(256/w):
        a = random_key()
        priv.append(a)

        for y in range(2**w-1):              #F
            a = sha256(a)

        pub.append(sha256(a))               #G (just in case we have a different f from g).

    elapsed_time = time.time() - start_time
    print elapsed_time
    
    return priv, pub    

def temp():

    priv = random_key()
    pub = priv
    for x in range(256):
        pub = sha256(pub)
    message = 'h'

    return priv, pub, message

def sign_wkey(priv, message):      #only works with 8 at present. havent separated the 'g' component yet.

    signature = []

    bin_msg = unhexlify(sha256(message))

    for y in range(len(priv)):

        s = priv[y]    

        for x in range(256-ord(bin_msg[y:y+1])):
            s = sha256(s)
        signature.append(s)

    return signature

def verify_wkey(signature, message, pub):

    verify = []

    bin_msg = unhexlify(sha256(message))
    
    for x in range(len(signature)):

        a = signature[x]
    
        for z in range(ord(bin_msg[x:x+1])-1):      #f is all but last hash..
                a=sha256(a)
        a = sha256(a)                               #g is the final hash, separate so can be changed..
        verify.append(a)
        
    if pub != verify:
        return False

    return True


def sign_lkey(priv, message):       #perform lamport signature
    
    signature = [] 

    bin_lmsg = unhexlify(sha256(message))

    z = 0
    for x in range (len(bin_lmsg)):
        l_byte = bin(ord(bin_lmsg[x]))[2:] #[2:][-1:]      #generate a binary string of 8 bits for each byte of 32/256.
        
        while len(l_byte) < 8:               #pad the zero's up to 8
                l_byte = '0'+ l_byte
        
        for y in range(0,8):
         if l_byte[-1:] == '0':
            signature.append(priv[z][0])
            l_byte = l_byte[:-1]
            z+=1
         else:
            signature.append(priv[z][1])
            l_byte = l_byte[:-1]
            z+=1

    return signature


def verify_lkey(signature, message, pub ):  #verify lamport signature

    bin_lmsg = unhexlify(sha256(message))

    verify = []

    z = 0

    for x in range (len(bin_lmsg)):
        l_byte = bin(ord(bin_lmsg[x]))[2:]   #generate a binary string of 8 bits for each byte of 32/256.
        
        while len(l_byte) < 8:               #pad the zero's up to 8
                l_byte = '0'+ l_byte
        
        for y in range(0,8):
         if l_byte[-1:] == '0':
            verify.append((sha256(signature[z]),pub[z][0]))
            l_byte = l_byte[:-1]
            z+=1
         else:
            verify.append((sha256(signature[z]),pub[z][1]))
            l_byte = l_byte[:-1]
            z+=1

    for p in range(len(verify)):
        if verify[p][0] == verify[p][1]:
            pass
        else:
            return False    

    return True

def random_lkey(numbers=256):      #create random lamport signature scheme keypair

    priv = []
    pub = []

    for x in range (numbers):
        a,b = random_key(), random_key()
        priv.append((a,b))
        pub.append((sha256(a),sha256(b)))


    return priv, pub


def random_qkey():      #create random merkle tree signature keypair

    priv = []
    for x in range(0,8):
        priv.append(random_key())

    tree = Merkle()
    private_key = tree.create_tree(priv)
    pub_key = priv[len(private_key)]
    return pub_key, private_key

# number of branches (n) up from base hash leaf constituents (l) to root is as follows:
# n=1 l(=1), n=2 l(>2<=4), n=3 l(>4<=8), n=4 l(>8<=16), n=5 l(>16<=32), n=6 l(>32<=64), n=7 l(<64>=128), n=8 l(>128<=256), n=9 l(>256<=512),


def random_wmss(signatures=4):  #create a w-ots mms with multiple signatures..
    
    data = []

    pubhashes = []

    for x in range(signatures):
        data.append(WOTS())

    for i in range(len(data)):
        pubhashes.append(data[i].pubhash)

    #print pubhashes

    a = Merkle(pub=pubhashes)



    return data, a.merkle_tree                 #array of wots classes full of data..


class WOTS():
    def __init__(self):
    
        self.concatpub = ""
        print 'New W-OTS keypair generation'
        self.priv, self.pub = random_wkey()
                
        self.concatpub = ''.join(self.pub)
        self.pubhash = sha256(self.concatpub)
        return

    def screen_print(self):
        print numlist(self.priv)
        print numlist(self.pub)
        print self.concatpub
        print self.pubhash
        return


class Merkle():

 def __init__(self, pub=[],priv=[],signatures=0):
    self.merkle_base = pub
    self.merkle_priv = priv
    self.signatures = len(priv)
    self.merkle_tree = []
    self.num_leaves = len(self.merkle_base)
    if not self.merkle_base:
        return
    else:
        self.create_tree()


 def route_proof(self):
    return 

 def create_tree(self):

    if self.num_leaves <= 2:
        num_branches = 1
    elif self.num_leaves >2 and self.num_leaves <=4:
        num_branches = 2
    elif self.num_leaves >4 and self.num_leaves <=8:
        num_branches = 3
    elif self.num_leaves >8 and self.num_leaves <=16:
        num_branches = 4
    elif self.num_leaves >16 and self.num_leaves <=32:
        num_branches = 5
    elif self.num_leaves >32 and self.num_leaves <=64:
        num_branches = 6
    elif self.num_leaves >64 and self.num_leaves <=128:
        num_branches = 7
    elif self.num_leaves >128 and self.num_leaves <=256:
        num_branches = 8
    elif self.num_leaves >256 and self.num_leaves <=512:
        num_branches = 9

    self.merkle_tree.append(self.merkle_base)

    hashlayer = self.merkle_base

    for x in range(num_branches):       #iterate through each layer of the merkle tree starting with the base layer
        temp_array = []
        cycles = len(hashlayer)%2 + len(hashlayer)/2
        #print 'branch cycle: ', str(x), ' - number of hashes / leaves:', self.num_leaves, ' - (pairs + modulo) per layer:', cycles
        y = 0
        for x in range(cycles):
            if y+1 == len(hashlayer):
             temp_array.append(str(hashlayer[y]))
            else:
             temp_array.append(sha256(str(hashlayer[y])+str(hashlayer[y+1])))
             y=y+2

        self.merkle_tree.append(temp_array)
        hashlayer = temp_array
    print 'Merkle tree created with '+str(self.num_leaves),' leaves, and '+str(num_branches)+' to root.'
    return self.merkle_tree

 def check_item(self):
     return