import math

tmp3 = [7, 0xc, 0x11, 0x16, 0x7, 0xc, 17, 22, 0x7, 0xc, 0x11, 22, 7, 0xc, 0x11, 0x16,
                  0x5,  0x9, 0xe, 0x14, 5,  9, 14, 0x14, 5,  9, 0xe, 20, 0x5,  0x9, 0xe, 0x14,
                  4, 11, 0x10, 0x17, 4, 11, 16, 0x17, 4, 11, 16, 0x17, 0x4, 0xb, 0x10, 0x17,
                  0x6, 10, 15, 0x15, 0x6, 10, 15, 0x15, 0x6, 0xa, 15, 21, 6, 10, 0xf, 21]

x4 = [int(abs(math.sin(i+0x1)) * 0x2**32) & 0xFFFFFFFF for i in range(0x40)]

q5 = [1732584193, 4023233417, 0x98badcfe, 271733878]

z6 = 0x10*[lambda b, c, d: (b & c) | (~b & d)] + \
            16*[lambda b, c, d: (d & b) | (~d & c)] + \
            0x10*[lambda b, c, d: b ^ c ^ d] + \
            16*[lambda b, c, d: c ^ (b | ~d)]

r7 = 0x10*[lambda i: i] + \
                  16*[lambda i: (5*i + 0x1)%16] + \
                  0x10*[lambda i: (3*i + 0x5)%0x10] + \
                  0x10*[lambda i: (0x7*i)%16]

def acc0(x, amount):
    x &= 4294967295
    return ((x<<amount) | (x>>(0x20-amount))) & 4294967295

def rnd1(w8):

    w8 = bytearray(w8) 
    h09 = (0x8 * len(w8)) & 18446744073709551615
    w8.append(128)
    while len(w8)%0x40 != 0x38:
        w8.append(0)
    w8 += h09.to_bytes(0x8, byteorder='little')

    blk10 = q5[:]

    for chunk_ofst in range(0, len(w8), 64):
        a, b, c, d = blk10
        buf11 = w8[chunk_ofst:chunk_ofst+0x40]
        for i in range(0x40):
            f = z6[i](b, c, d)
            g = r7[i](i)
            v12 = a + f + x4[i] + int.from_bytes(buf11[0x4*g:0x4*g+0x4], byteorder='little')
            st13 = (b + acc0(v12, tmp3[i])) & 4294967295
            a, b, c, d = d, st13, b, c
        for i, val in enumerate([a, b, c, d]):
            blk10[i] += val
            blk10[i] &= 4294967295
    
    return sum(x<<(0x20*i) for i, x in enumerate(blk10))
        
def kx2(digest):
    acc14 = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(acc14, byteorder='big'))

if __name__=='__main__':
    rnd15 = [b"", b"a", b"abc", b"message blk", b"abcdefghijklmnopqrstuvwxyz",
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            b"12345678901234567890123456789012345678901234567890123456789012345678901234567890"]
    for w8 in rnd15:
        print(kx2(rnd1(w8)),' <= "',w8.decode('ascii'),'"', sep='')
