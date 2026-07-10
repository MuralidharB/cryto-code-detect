def luhn_checksum(number: str) -> int:
    digits = [int(d) for d in number if d.isdigit()]
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10

def is_valid(number: str) -> bool:
    return luhn_checksum(number) == 0

def check_digit(partial: str) -> int:
    s = luhn_checksum(partial + "0")
    return (10 - s) % 10

if __name__ == "__main__":
    card = "79927398713"
    print("valid:", is_valid(card))
    print("check digit for 7992739871:", check_digit("7992739871"))
