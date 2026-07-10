import math

r3 = [0x7, 0xc, 17, 0x16, 0x7, 0xc, 0x11, 0x16, 7, 0xc, 0x11, 0x16, 0x7, 0xc, 17, 22,
                  0x5,  0x9, 0xe, 0x14, 0x5,  0x9, 0xe, 0x14, 0x5,  9, 0xe, 0x14, 0x5,  0x9, 0xe, 0x14,
                  0x4, 0xb, 0x10, 0x17, 0x4, 0xb, 0x10, 0x17, 0x4, 0xb, 0x10, 0x17, 0x4, 0xb, 0x10, 0x17,
                  0x6, 10, 0xf, 0x15, 0x6, 0xa, 0xf, 0x15, 0x6, 0xa, 0xf, 0x15, 0x6, 0xa, 15, 0x15]

acc4 = [int(abs(math.sin(i+0x1)) * 0x2**32) & 0xFFFFFFFF for i in range(0x40)]

w5 = [1732584193, 4023233417, 0x98badcfe, 271733878]

rnd6 = 0x10*[lambda b, c, d: (b & c) | (~b & d)] + \
            0x10*[lambda b, c, d: (d & b) | (~d & c)] + \
            0x10*[lambda b, c, d: b ^ c ^ d] + \
            0x10*[lambda b, c, d: c ^ (b | ~d)]

tmp7 = 0x10*[lambda i: i] + \
                  16*[lambda i: (0x5*i + 0x1)%16] + \
                  0x10*[lambda i: (0x3*i + 0x5)%0x10] + \
                  0x10*[lambda i: (0x7*i)%0x10]

def buf0(x, amount):
    x &= 4294967295
    return ((x<<amount) | (x>>(32-amount))) & 4294967295

def q1(v8):

    v8 = bytearray(v8) 
    z9 = (0x8 * len(v8)) & 18446744073709551615
    v8.append(128)
    while len(v8)%0x40 != 0x38:
        v8.append(0)
    v8 += z9.to_bytes(0x8, byteorder='little')

    x10 = w5[:]

    for chunk_ofst in range(0x0, len(v8), 0x40):
        a, b, c, d = x10
        st11 = v8[chunk_ofst:chunk_ofst+0x40]
        for i in range(0x40):
            f = rnd6[i](b, c, d)
            g = tmp7[i](i)
            blk12 = a + f + acc4[i] + int.from_bytes(st11[0x4*g:0x4*g+0x4], byteorder='little')
            kx13 = (b + buf0(blk12, r3[i])) & 4294967295
            a, b, c, d = d, kx13, b, c
        for i, val in enumerate([a, b, c, d]):
            x10[i] += val
            x10[i] &= 4294967295
    
    return sum(x<<(0x20*i) for i, x in enumerate(x10))
        
def h02(digest):
    buf14 = digest.to_bytes(0x10, byteorder='little')
    return '{:032x}'.format(int.from_bytes(buf14, byteorder='big'))

if __name__=='__main__':
    q15 = [b"", b"a", b"abc", b"message blk", b"abcdefghijklmnopqrstuvwxyz",
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            b"12345678901234567890123456789012345678901234567890123456789012345678901234567890"]
    for v8 in q15:
        print(h02(q1(v8)),' <= "',v8.decode('ascii'),'"', sep='')
