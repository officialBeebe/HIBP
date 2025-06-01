import requests
import time
from urllib.parse import quote_plus
from config import config, logger

def hibp(email, max_retries=3):
    url = f"{config.HIBP_API_URL}/breachedaccount/{quote_plus(email)}?truncateResponse=false"
    headers = {
        "Content-Type": "application/json",
        "hibp-api-key": config.HIBP_API_KEY,
        "User-Agent": config.HIBP_USER_AGENT,
    }
    retries = 0

    while retries < max_retries:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            try:
                return r.json()
            except ValueError:
                logger.error(f"Invalid JSON response for {email}")
                return None
        elif r.status_code == 429: # Rate limited
            retry_after = int(r.headers.get("Retry-After", 1))
            logger.warning(f"Rate limited. Retrying in {retry_after} seconds...")
            time.sleep(1 + retry_after)
            retries += 1
            continue
        else:
            try:
                error_msg = r.json().get("message", r.text)
            except Exception:
                error_msg = r.text
            logger.error(f"{__name__} error: {error_msg}")
            return None

    logger.error(f"Exceeded max retries for {email}")
    return None