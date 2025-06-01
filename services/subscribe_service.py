from sqlalchemy import text
from db import SessionLocal
from config import logger

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