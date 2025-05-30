from datetime import datetime
import email
import os
import time
import logging

from flask import Flask
from flask import request
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import create_engine, text
import dotenv
from urllib.parse import quote_plus
import requests
from sqlalchemy.orm import scoped_session, sessionmaker

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

def test_db(data):
    session = SessionLocal()
    try:
        with session.begin():
            session.execute(text("insert into test (test_column) values (:data)"), {"data": data})
    except Exception as e:
        session.rollback()
        logger.error(f"DB test insert failed: {e}")
        raise
    finally:
        session.close()


def touch(email, timestamp: datetime):
    session = SessionLocal()

    try:
        with session.begin():
            session.execute(text("update account set last_touch=:timestamp where email=:email"), {"email": email, "timestamp": timestamp})
    except Exception as e:
        session.rollback()
        logger.error(f"DB account update failed: {e}")
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


def ses_alert(results):
    pass


@app.post("/test")
def test():
    data = request.get_json()
    test_db(data["test"])
    return {"status": "success"}

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    def _subscribe(email):
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

        # Run hibp() for new subscriber's email
        results = hibp(email)
        if results:
            ses_alert(results)

        return {"status": "subscribed", "breaches": results}
        # return '''
        #     <p>Subscription confirmed. Any breaches tied to your email will be sent to you shortly. To ensure you don't miss future alerts, please check your spam folder and whitelist our address.</p>
        # '''

    SUBSCRIBER_FORM = '''
        <form method="POST">
            <p>Subscribe to receive automatic alerts about security breaches associated with your email address.</p>
            <input name="email" type="email" />
            <input type="submit" value="Subscribe" />
        </form>
    '''

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        _email = data.get('email')

        if not _email:
            return "Email is required", 400

        try:
            email_info = validate_email(_email)
            _email = email_info.normalized
        except EmailNotValidError as e:
            return (str(e), 400)


        return _subscribe(_email)
    else:
        return SUBSCRIBER_FORM

@app.get('/hibp/<email>')
def _hibp(email):
    return hibp(email)


if __name__ == '__main__':
    app.run()
