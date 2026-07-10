"""Geohash encoding of a latitude/longitude pair.

Interleaves the bits of the two coordinate ranges and maps groups of
five bits to a base-32 alphabet, producing a short string whose prefix
length controls spatial precision (useful for proximity bucketing).
"""

_ALPHABET = "0123456789bcdefghjkmnpqrstuvwxyz"


def encode(lat, lon, precision=9):
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    bits = []
    even = True
    while len(bits) < precision * 5:
        if even:
            mid = sum(lon_range) / 2
            if lon >= mid:
                bits.append(1)
                lon_range[0] = mid
            else:
                bits.append(0)
                lon_range[1] = mid
        else:
            mid = sum(lat_range) / 2
            if lat >= mid:
                bits.append(1)
                lat_range[0] = mid
            else:
                bits.append(0)
                lat_range[1] = mid
        even = not even

    out = []
    for i in range(0, len(bits), 5):
        idx = 0
        for b in bits[i:i + 5]:
            idx = (idx << 1) | b
        out.append(_ALPHABET[idx])
    return "".join(out)
