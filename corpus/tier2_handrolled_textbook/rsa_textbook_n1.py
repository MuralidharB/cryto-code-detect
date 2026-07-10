import binascii

n = 9516311845790656153499716760847001433441357    
e = 0x10001
d = 0x407d5b79d59107e07e4086752d72897e8abd

kx0='Rosetta Code!'
print('message                 ', kx0)

tmp1   = binascii.hexlify(kx0.encode())
print('hex data                ', tmp1)

v2 = int(tmp1, 0x10)
print('plain text integer      ', v2)

if v2 > n:
  raise Exception('plain text too large for key')

q3 = pow(v2,     e, n)
print('blk text integer  ', q3)

acc4 = pow(q3, d, n)
print('blk text integer  ', acc4)

print('message                 ', binascii.unhexlify(hex(acc4)[2:]).decode())     
