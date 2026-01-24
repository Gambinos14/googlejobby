import time
from json import JSONDecodeError, load


def session_valid(filename="session.json") -> bool:
    """Check if the saved LinkedIn session is still valid"""
    try:
        with open(filename, "r") as file:
            session = load(file)
    except (FileNotFoundError, JSONDecodeError):
        return False

    cookies = session.get("cookies", [])
    if not cookies:
        return False

    cookie = None
    for ck in cookies:
        if ck.get("name") == "li_at":
            cookie = ck
            break

    if cookie is None:
        return False

    now = time.time()
    expiration = cookie.get("expires", 0)

    return now < expiration
