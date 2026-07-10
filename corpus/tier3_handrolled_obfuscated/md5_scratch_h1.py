import math

st3 = [0x7, 0xc, 0x11, 0x16, 0x7, 0xc, 0x11, 0x16, 7, 0xc, 0x11, 0x16, 0x7, 0xc, 0x11, 0x16,
                  0x5,  0x9, 0xe, 0x14, 0x5,  0x9, 0xe, 0x14, 5,  0x9, 14, 20, 0x5,  9, 0xe, 20,
                  0x4, 0xb, 0x10, 23, 0x4, 0xb, 0x10, 0x17, 0x4, 0xb, 16, 0x17, 4, 11, 16, 0x17,
                  6, 0xa, 0xf, 0x15, 0x6, 0xa, 0xf, 21, 0x6, 0xa, 0xf, 0x15, 0x6, 10, 0xf, 0x15]

x4 = [int(abs(math.sin(i+1)) * 0x2**0x20) & 0xFFFFFFFF for i in range(64)]

h05 = [1732584193, 0xefcdab89, 0x98badcfe, 0x10325476]

w6 = 0x10*[lambda b, c, d: (b & c) | (~b & d)] + \
            0x10*[lambda b, c, d: (d & b) | (~d & c)] + \
            0x10*[lambda b, c, d: b ^ c ^ d] + \
            0x10*[lambda b, c, d: c ^ (b | ~d)]

buf7 = 0x10*[lambda i: i] + \
                  16*[lambda i: (0x5*i + 0x1)%16] + \
                  16*[lambda i: (0x3*i + 0x5)%0x10] + \
                  0x10*[lambda i: (0x7*i)%0x10]

def blk0(x, amount):
    x &= 4294967295
    return ((x<<amount) | (x>>(0x20-amount))) & 4294967295

def kx1(z8):

    z8 = bytearray(z8) 
    acc9 = (8 * len(z8)) & 18446744073709551615
    z8.append(128)
    while len(z8)%0x40 != 0x38:
        z8.append(0x0)
    z8 += acc9.to_bytes(0x8, byteorder='little')

    tmp10 = h05[:]

    for chunk_ofst in range(0x0, len(z8), 0x40):
        a, b, c, d = tmp10
        q11 = z8[chunk_ofst:chunk_ofst+0x40]
        for i in range(0x40):
            f = w6[i](b, c, d)
            g = buf7[i](i)
            v12 = a + f + x4[i] + int.from_bytes(q11[0x4*g:0x4*g+0x4], byteorder='little')
            r13 = (b + blk0(v12, st3[i])) & 0xFFFFFFFF
            a, b, c, d = d, r13, b, c
        for i, val in enumerate([a, b, c, d]):
            tmp10[i] += val
            tmp10[i] &= 4294967295
    
    return sum(x<<(0x20*i) for i, x in enumerate(tmp10))
        
def rnd2(digest):
    blk14 = digest.to_bytes(0x10, byteorder='little')
    return '{:032x}'.format(int.from_bytes(blk14, byteorder='big'))

if __name__=='__main__':
    kx15 = [b"", b"a", b"abc", b"message blk", b"abcdefghijklmnopqrstuvwxyz",
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            b"12345678901234567890123456789012345678901234567890123456789012345678901234567890"]
    for z8 in kx15:
        print(rnd2(kx1(z8)),' <= "',z8.decode('ascii'),'"', sep='')
