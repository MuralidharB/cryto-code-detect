def isbn13_check_digit(first12: str) -> int:
    digits = [int(c) for c in first12 if c.isdigit()]
    if len(digits) != 12:
        raise ValueError("need exactly 12 digits")
    total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    return (10 - (total % 10)) % 10

def is_valid_isbn13(isbn: str) -> bool:
    digits = [int(c) for c in isbn if c.isdigit()]
    if len(digits) != 13:
        return False
    return isbn13_check_digit("".join(map(str, digits[:12]))) == digits[12]

if __name__ == "__main__":
    print("check digit:", isbn13_check_digit("978030640615"))
    print("valid:", is_valid_isbn13("9780306406157"))
