import re
from datetime import datetime
import email
import os
import time
import logging
import asyncio

from flask import Flask
from flask import request
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import create_engine, text
import dotenv
from urllib.parse import quote_plus
import requests
from sqlalchemy.orm import scoped_session, sessionmaker
from pgnotify import await_pg_notifications

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    HIBP_API_URL = os.getenv("HIBP_API_URL")
    HIBP_API_KEY = os.getenv("HIBP_API_KEY")
    HIBP_USER_AGENT = os.getenv("HIBP_USER_AGENT")

    @property
    def db_url(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

config = Config()
engine = create_engine(config.db_url, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(bind=engine))
app = Flask(__name__)


def touch(email, timestamp: datetime):
    session = SessionLocal()

    try:
        with session.begin():
            session.execute(text("update account set last_touch=:timestamp where email=:email"), {"email": email, "timestamp": timestamp})
    except Exception as e:
        session.rollback()
        logger.error(f"DB account.last_touch update failed: {e}")
        raise
    finally:
        session.close()


def get_touch(email):
    session = SessionLocal()

    try:
        with session.begin():
            last_touch = session.execute(text("select last_touch from account where email=:email"), {"email": email})
            return last_touch.scalar()
    except Exception as e:
        session.rollback()
        logger.error(f"DB account.last_touch select failed: {e}")
        raise
    finally:
        session.close()


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
                touch(email, datetime.now())
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


def parse_urls(string):
    url_pattern = re.compile(
        r'(https?://[^\s]+)',
        re.IGNORECASE
    )

    matches = url_pattern.findall(string)
    return matches


def upsert_breach(breach):
    session = SessionLocal()
    try:
        session.execute(text("""
            INSERT INTO breach (
            name, title, domain, breach_date, added_date, modified_date, 
            pwn_count, description, logo_path, data_classes, is_verified,
            is_fabricated, is_sensitive, is_retired, is_spam_list, is_malware, 
            is_subscription_free, is_stealer_log
            )
            VALUES (:name, :title, :domain, :breach_date, :added_date, :modified_date, 
                   :pwn_count, :description, :logo_path, :data_classes, :is_verified, 
                   :is_fabricated, :is_sensitive, is_retired, :is_spam_list, :is_malware, 
                   :is_subscription_free, is_stealer_log
            )
            ON CONFLICT (name) DO UPDATE SET
                title = EXCLUDED.title,
                domain = EXCLUDED.domain,
                breach_date = EXCLUDED.added_date,
                added_date = EXCLUDED.modified_date,
                modified_date = EXCLUDED.modified_date,
                pwn_count = EXCLUDED.pwn_count,
                description = EXCLUDED.description,
                logo_path = EXCLUDED.logo_path,
                data_classes = EXCLUDED.data_classes,
                is_verified = EXCLUDED.is_verified,
                is_fabricated = EXCLUDED.is_fabricated,
                is_sensitive = EXCLUDED.is_sensitive,
                is_retired = EXCLUDED.is_retired,
                is_spam_list = EXCLUDED.is_spam_list,
                is_malware = EXCLUDED.is_malware,
                is_subscription_free = EXCLUDED.is_subscription_free,
                is_stealer_log = EXCLUDED.is_stealer_log
            WHERE
                breach.title IS DISTINCT FROM EXCLUDED.title OR
                breach.domain IS DISTINCT FROM EXCLUDED.domain OR
                breach.breach_date IS DISTINCT FROM EXCLUDED.added_date OR
                breach.added_date IS DISTINCT FROM EXCLUDED.modified_date OR
                breach.modified_date IS DISTINCT FROM EXCLUDED.modified_date OR
                breach.pwn_count IS DISTINCT FROM EXCLUDED.pwn_count OR
                breach.description IS DISTINCT FROM EXCLUDED.description OR
                breach.logo_path IS DISTINCT FROM EXCLUDED.logo_path OR
                breach.data_clases IS DISTINCT FROM EXCLUDED.data_classes OR
                breach.is_verified IS DISTINCT FROM EXCLUDED.is_verified OR
                breach.is_fabricated IS DISTINCT FROM EXCLUDED.is_fabricated OR
                breach.is_sensitive IS DISTINCT FROM EXCLUDED.is_sensitive OR
                breach.is_retired IS DISTINCT FROM EXCLUDED.is_retired OR
                breach.is_spam_list IS DISTINCT FROM EXCLUDED.spam_list OR
                breach.is_malware IS DISTINCT FROM EXCLUDED.malware OR
                breach.is_subscription_free IS DISTINCT FROM EXCLUDED.subscription_free OR
                breach.is_stealer_log IS DISTINCT FROM EXCLUDED.stealer_log 
        """), {
            'name': breach['name'],
            'title': breach['title'],
            'domain': breach['domain'],
            'breach_date': breach['added_date'],
            'added_date': breach['modified_date'],
            'modified_date': breach['modified_date'],
            'pwn_count': breach['pwn_count'],
            'description': breach['description'],
            'logo_path': breach['logo_path'],
            'data_classes': breach['data_classes'],
            'is_verified': breach['is_verified'],
            'is_fabricated': breach['is_fabricated'],
            'is_sensitive': breach['is_sensitive'],
            'is_retired': breach['is_retired'],
            'is_spam_list': breach['is_spam_list'],
            'is_malware': breach['is_malware'],
            'is_subscription_free': breach['is_subscription_free'],
            'is_stealer_log': breach['is_stealer_log']
        })
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to upsert breach {breach.get('Name')}: {e}")
        raise
    finally:
        session.close()


def insert_account_breach():
    session = SessionLocal()
    try:
        pass
    except Exception as e:
        pass
    finally:
        session.close()


def alert(email, results):
    # Trigger AWS SES alert for an email
    pass


def subscribe(email):
    # Add account to Postgres
    session = SessionLocal()
    try:
        with session.begin():
            session.execute(text("insert into account (email) values (:email)"), {"email": email})
    except Exception as e:
        session.rollback()
        logger.error(f"DB account insert failed: {e}")
        raise
    finally:
        session.close()


def unsubscribe(email):
    session = SessionLocal()
    try:
        with session.begin():
            session.execute(text("delete from account where email=:email"), {"email": email})
    except Exception as e:
        session.rollback()
        logger.error(f"DB account delete failed: {e}")
        raise
    finally:
        session.close()

@app.route('/', methods=['GET'])
def index_route():
    return '''
            <h1>Welcome to the Have I Been Pwned Alert App!</h1>
            <p><a href="/subscribe">Subscribe</a> | <a href="/unsubscribe">Unsubscribe</a></p>
        '''


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe_route():
    subscribe_html = '''
                <form method="POST">
                    <p>Subscribe to receive automatic alerts about security breaches associated with your email address.</p>
                    <input name="email" type="email" />
                    <input type="submit" value="Subscribe" />
                </form>
            '''

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')

        if not email:
            return "Email is required", 400

        try:
            email_info = validate_email(email)
            email = email_info.normalized
        except EmailNotValidError as e:
            return (str(e), 400)

        try:
            subscribe(email)
        except Exception as e:
            return f"Subscribe failed: {e}", 500

        return f"Subscribed {email}", 200

    return subscribe_html


@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe_route():
    form_html = '''
            <form method="POST">
                <p>Unsubscribe from breach alerts.</p>
                <input name="email" type="email" required />
                <input type="submit" value="Unsubscribe" />
            </form>
        '''

    if request.method == 'POST':
        data = request.form
        email = data.get('email')

        if not email:
            return "Email is required", 400

        try:
            email_info = validate_email(email)
            email = email_info.normalized
        except EmailNotValidError as e:
            return str(e), 400

        try:
            unsubscribe(email)
        except Exception as e:
            return f"Unsubscribe failed: {e}", 500

        return f"Unsubscribed {email}", 200

    return form_html


@app.route('/hibp', methods=['POST'])
def hibp_route():
    email = request.get_json()['email']
    return hibp(email)


if __name__ == '__main__':
    app.run()
