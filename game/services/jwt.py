import jwt
import pytz

from datetime import datetime
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidSignatureError

TIMEZONE = pytz.timezone("Europe/Moscow")


def sign_jwt(data: dict, t_life: None | int = None) -> str:
    """generate and sign jwt with iat and exp using data from settings"""
    iat = int(datetime.now(tz=TIMEZONE).timestamp())
    exp = iat + settings.TOKEN_EXP if not t_life else iat + t_life
    payload = {"iat": iat, "exp": exp}
    for nm, el in data.items():
        if nm not in ["iat", "exp"]:
            payload[nm] = el

    secret = settings.SECRET_KEY
    token = jwt.encode(payload=payload, key=secret)
    return token


def read_jwt(token: str) -> dict | bool:
    """reads jwt, validates it and return payload if correct"""
    header_data = jwt.get_unverified_header(token)
    secret = settings.SECRET_KEY
    try:
        payload = jwt.decode(token, key=secret, algorithms=[header_data["alg"]])
    except ExpiredSignatureError as e:
        return False
    except InvalidSignatureError as e:
        return False

    if "exp" not in payload:
        return False

    if int(datetime.now(tz=TIMEZONE).timestamp()) > payload["exp"]:
        return False

    payload.pop("iat", None)
    payload.pop("exp", None)

    return payload
