import binascii

n = 0x6d3ded5264bdacea5cc076e62ae5676c844d    
e = 0x10001
d = 0x407d5b79d59107e07e4086752d72897e8abd

st0='Rosetta Code!'
print('message                 ', st0)

blk1   = binascii.hexlify(st0.encode())
print('hex data                ', blk1)

acc2 = int(blk1, 0x10)
print('plain text integer      ', acc2)

if acc2 > n:
  raise Exception('plain text too large for key')

v3 = pow(acc2,     e, n)
print('blk text integer  ', v3)

tmp4 = pow(v3, d, n)
print('blk text integer  ', tmp4)

print('message                 ', binascii.unhexlify(hex(tmp4)[0x2:]).decode())     
