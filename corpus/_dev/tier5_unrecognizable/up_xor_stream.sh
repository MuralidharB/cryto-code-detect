#!/bin/sh
# Reads stdin and combines each byte with a repeating key using od/printf.
# Running it a second time with the same key restores the input.

key="$1"
[ -z "$key" ] && { echo "usage: $0 <key>" >&2; exit 1; }

klen=${#key}
i=0
while [ "$i" -lt "$klen" ]; do
    off=$((i + 1))
    kb=$(printf '%s' "$key" | cut -c "$off" | od -An -tu1 | tr -d ' \n')
    eval "kbyte_$i=$kb"
    i=$((i + 1))
done

# collect input bytes as decimals, then process in the main shell so the
# position counter survives across bytes.
bytes=$(od -An -tu1 -v | tr -s ' \n' ' ')

pos=0
for byte in $bytes; do
    idx=$((pos % klen))
    eval "kb=\$kbyte_$idx"
    out=$((byte ^ kb))
    printf '%b' "$(printf '\\0%o' "$out")"
    pos=$((pos + 1))
done
