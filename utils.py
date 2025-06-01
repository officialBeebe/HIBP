import re

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