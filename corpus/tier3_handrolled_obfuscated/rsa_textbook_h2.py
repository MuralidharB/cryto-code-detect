import binascii

n = 0x6d3ded5264bdacea5cc076e62ae5676c844d    
e = 65537
d = 5617843187844953170308463622230283376298685

rnd0='Rosetta Code!'
print('message                 ', rnd0)

acc1   = binascii.hexlify(rnd0.encode())
print('hex data                ', acc1)

x2 = int(acc1, 0x10)
print('plain text integer      ', x2)

if x2 > n:
  raise Exception('plain text too large for key')

w3 = pow(x2,     e, n)
print('blk text integer  ', w3)

tmp4 = pow(w3, d, n)
print('blk text integer  ', tmp4)

print('message                 ', binascii.unhexlify(hex(tmp4)[0x2:]).decode())     
