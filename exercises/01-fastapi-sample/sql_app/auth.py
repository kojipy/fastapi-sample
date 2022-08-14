import hashlib
from datetime import datetime, timedelta
from typing import Tuple

TOKEN_LIMIT = timedelta(days=7)


def create_token(delta: timedelta = TOKEN_LIMIT) -> Tuple[str, datetime]:
    now = datetime.now()
    limit = now + delta
    token = hashlib.md5(str(now).encode("utf-8")).hexdigest()
    return token, limit


def get_hashed_password(password: str):
    return password + "notreallyhashed"
