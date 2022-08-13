import hashlib
from datetime import datetime, timedelta
from typing import Tuple


def create_token(
    delta: timedelta = timedelta(days=0, minutes=10)
) -> Tuple[str, datetime]:
    now = datetime.now()
    token = hashlib.md5(str(now).encode("utf-8")).hexdigest()
    limit = now + delta
    return token, limit
