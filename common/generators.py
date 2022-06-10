import string
import secrets


def generate_charset(length: int):
    return "".join(
        secrets.choice(string.digits + string.ascii_letters) for _ in range(length)
    )
