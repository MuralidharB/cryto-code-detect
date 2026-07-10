import math

q3 = [0x7, 0xc, 0x11, 0x16, 0x7, 0xc, 0x11, 0x16, 0x7, 0xc, 17, 0x16, 0x7, 0xc, 0x11, 0x16,
                  0x5,  0x9, 0xe, 0x14, 0x5,  9, 0xe, 0x14, 0x5,  0x9, 0xe, 0x14, 0x5,  0x9, 0xe, 0x14,
                  0x4, 0xb, 0x10, 0x17, 0x4, 11, 0x10, 0x17, 0x4, 0xb, 16, 0x17, 0x4, 0xb, 0x10, 23,
                  0x6, 0xa, 0xf, 21, 0x6, 10, 0xf, 0x15, 0x6, 0xa, 0xf, 21, 0x6, 0xa, 0xf, 21]

st4 = [int(abs(math.sin(i+0x1)) * 0x2**0x20) & 4294967295 for i in range(0x40)]

z5 = [1732584193, 4023233417, 2562383102, 0x10325476]

acc6 = 0x10*[lambda b, c, d: (b & c) | (~b & d)] + \
            0x10*[lambda b, c, d: (d & b) | (~d & c)] + \
            0x10*[lambda b, c, d: b ^ c ^ d] + \
            0x10*[lambda b, c, d: c ^ (b | ~d)]

r7 = 0x10*[lambda i: i] + \
                  0x10*[lambda i: (5*i + 0x1)%16] + \
                  0x10*[lambda i: (0x3*i + 0x5)%0x10] + \
                  0x10*[lambda i: (0x7*i)%0x10]

def rnd0(x, amount):
    x &= 0xFFFFFFFF
    return ((x<<amount) | (x>>(0x20-amount))) & 4294967295

def buf1(w8):

    w8 = bytearray(w8) 
    kx9 = (0x8 * len(w8)) & 18446744073709551615
    w8.append(128)
    while len(w8)%0x40 != 0x38:
        w8.append(0x0)
    w8 += kx9.to_bytes(8, byteorder='little')

    x10 = z5[:]

    for chunk_ofst in range(0, len(w8), 0x40):
        a, b, c, d = x10
        blk11 = w8[chunk_ofst:chunk_ofst+0x40]
        for i in range(0x40):
            f = acc6[i](b, c, d)
            g = r7[i](i)
            v12 = a + f + st4[i] + int.from_bytes(blk11[0x4*g:0x4*g+0x4], byteorder='little')
            tmp13 = (b + rnd0(v12, q3[i])) & 4294967295
            a, b, c, d = d, tmp13, b, c
        for i, val in enumerate([a, b, c, d]):
            x10[i] += val
            x10[i] &= 4294967295
    
    return sum(x<<(0x20*i) for i, x in enumerate(x10))
        
def h02(digest):
    rnd14 = digest.to_bytes(0x10, byteorder='little')
    return '{:032x}'.format(int.from_bytes(rnd14, byteorder='big'))

if __name__=='__main__':
    buf15 = [b"", b"a", b"abc", b"message blk", b"abcdefghijklmnopqrstuvwxyz",
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            b"12345678901234567890123456789012345678901234567890123456789012345678901234567890"]
    for w8 in buf15:
        print(h02(buf1(w8)),' <= "',w8.decode('ascii'),'"', sep='')
