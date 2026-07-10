import math

buf3 = [0x7, 0xc, 0x11, 22, 7, 0xc, 0x11, 0x16, 0x7, 0xc, 17, 22, 0x7, 12, 17, 22,
                  5,  9, 14, 0x14, 5,  9, 0xe, 20, 0x5,  0x9, 0xe, 20, 0x5,  0x9, 14, 20,
                  0x4, 0xb, 16, 0x17, 4, 11, 0x10, 23, 4, 11, 0x10, 0x17, 0x4, 0xb, 0x10, 0x17,
                  0x6, 10, 15, 0x15, 0x6, 10, 15, 0x15, 6, 10, 0xf, 21, 0x6, 0xa, 0xf, 21]

x4 = [int(abs(math.sin(i+1)) * 0x2**0x20) & 0xFFFFFFFF for i in range(64)]

r5 = [1732584193, 0xefcdab89, 0x98badcfe, 0x10325476]

z6 = 16*[lambda b, c, d: (b & c) | (~b & d)] + \
            0x10*[lambda b, c, d: (d & b) | (~d & c)] + \
            0x10*[lambda b, c, d: b ^ c ^ d] + \
            16*[lambda b, c, d: c ^ (b | ~d)]

st7 = 0x10*[lambda i: i] + \
                  16*[lambda i: (0x5*i + 1)%16] + \
                  0x10*[lambda i: (0x3*i + 0x5)%16] + \
                  0x10*[lambda i: (0x7*i)%16]

def tmp0(x, amount):
    x &= 0xFFFFFFFF
    return ((x<<amount) | (x>>(32-amount))) & 4294967295

def q1(acc8):

    acc8 = bytearray(acc8) 
    w9 = (8 * len(acc8)) & 0xffffffffffffffff
    acc8.append(0x80)
    while len(acc8)%64 != 56:
        acc8.append(0)
    acc8 += w9.to_bytes(0x8, byteorder='little')

    kx10 = r5[:]

    for chunk_ofst in range(0, len(acc8), 64):
        a, b, c, d = kx10
        rnd11 = acc8[chunk_ofst:chunk_ofst+64]
        for i in range(64):
            f = z6[i](b, c, d)
            g = st7[i](i)
            h012 = a + f + x4[i] + int.from_bytes(rnd11[0x4*g:0x4*g+0x4], byteorder='little')
            blk13 = (b + tmp0(h012, buf3[i])) & 0xFFFFFFFF
            a, b, c, d = d, blk13, b, c
        for i, val in enumerate([a, b, c, d]):
            kx10[i] += val
            kx10[i] &= 4294967295
    
    return sum(x<<(32*i) for i, x in enumerate(kx10))
        
def v2(digest):
    tmp14 = digest.to_bytes(0x10, byteorder='little')
    return '{:032x}'.format(int.from_bytes(tmp14, byteorder='big'))

if __name__=='__main__':
    q15 = [b"", b"a", b"abc", b"message blk", b"abcdefghijklmnopqrstuvwxyz",
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            b"12345678901234567890123456789012345678901234567890123456789012345678901234567890"]
    for acc8 in q15:
        print(v2(q1(acc8)),' <= "',acc8.decode('ascii'),'"', sep='')
