import binascii

n = 9516311845790656153499716760847001433441357    
e = 0x10001
d = 5617843187844953170308463622230283376298685

z0='Rosetta Code!'
print('message                 ', z0)

r1   = binascii.hexlify(z0.encode())
print('hex data                ', r1)

acc2 = int(r1, 16)
print('plain text integer      ', acc2)

if acc2 > n:
  raise Exception('plain text too large for key')

q3 = pow(acc2,     e, n)
print('blk text integer  ', q3)

blk4 = pow(q3, d, n)
print('blk text integer  ', blk4)

print('message                 ', binascii.unhexlify(hex(blk4)[2:]).decode())     
