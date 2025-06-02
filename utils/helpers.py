import re

from email_validator import validate_email, EmailNotValidError


def extract_and_validate_email(data):
    email = data.get('email')
    if not email:
        raise ValueError("Email is required")
    try:
        email_info = validate_email(email)
        return email_info.normalized
    except EmailNotValidError as e:
        raise ValueError(str(e))


def parse_urls(string):
    url_pattern = re.compile(
        r'(https?://[^\s]+)',
        re.IGNORECASE
    )

    matches = url_pattern.findall(string)
    return matches


def alert(email, results):
    # Trigger AWS SES alert for an email
    pass
