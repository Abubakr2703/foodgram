import string

ALPHABET = string.digits + string.ascii_letters
BASE = len(ALPHABET)


def encode_base62(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    res = []
    while num:
        num, rem = divmod(num, BASE)
        res.append(ALPHABET[rem])
    return ''.join(reversed(res))


def decode_base62(s: str) -> int:
    num = 0
    for ch in s:
        num = num * BASE + ALPHABET.index(ch)
    return num
