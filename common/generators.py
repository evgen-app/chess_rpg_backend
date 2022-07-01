import string
import secrets

from random import randint


def generate_charset(length: int):
    return "".join(
        secrets.choice(string.digits + string.ascii_letters) for _ in range(length)
    )


def gen_ton():
    return int("".join([str(randint(0, 9)) for _ in range(48)]))
