#!/usr/bin/awk -f
# Transforms input bytes under an argument passed as -v arg=...
# Reads bytes as space-separated decimal (od -An -tu1) and emits the
# transformed bytes the same way. Applying it twice restores the input.

BEGIN {
    if (arg == "") { print "supply -v arg=..." > "/dev/stderr"; exit 1 }
    for (c = 0; c < 256; c++) _ord[sprintf("%c", c)] = c
    alen = split_arg()
    # derive a rolling state from the argument
    state = alen
    for (i = 0; i < alen; i++) state = (state * 31 + ab[i]) % 256
    pos = 0
}

function split_arg(   n, i, c) {
    n = length(arg)
    for (i = 1; i <= n; i++) {
        c = substr(arg, i, 1)
        ab[i - 1] = ord(c)
    }
    return n
}

function ord(ch) {
    return _ord[ch]
}

{
    for (f = 1; f <= NF; f++) {
        b = $f + 0
        state = (state * 1103515245 + 12345 + ab[pos % alen]) % 65536
        ks = int(state / 256) % 256
        out = combine(b, ks)
        printf("%d ", out)
        pos++
    }
}

function combine(a, c,   r, bit, av, cv) {
    r = 0; bit = 1
    for (i = 0; i < 8; i++) {
        av = a % 2; cv = c % 2
        if (av != cv) r += bit
        a = int(a / 2); c = int(c / 2); bit *= 2
    }
    return r
}

END { printf("\n") }
