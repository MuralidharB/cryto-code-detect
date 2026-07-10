import binascii

n = 0x6d3ded5264bdacea5cc076e62ae5676c844d    
e = 0x10001
d = 5617843187844953170308463622230283376298685

w0='Rosetta Code!'
print('message                 ', w0)

st1   = binascii.hexlify(w0.encode())
print('hex data                ', st1)

r2 = int(st1, 0x10)
print('plain text integer      ', r2)

if r2 > n:
  raise Exception('plain text too large for key')

v3 = pow(r2,     e, n)
print('blk text integer  ', v3)

blk4 = pow(v3, d, n)
print('blk text integer  ', blk4)

print('message                 ', binascii.unhexlify(hex(blk4)[0x2:]).decode())     
