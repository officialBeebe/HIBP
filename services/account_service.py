from sqlalchemy import text
from db import SessionLocal
from config import logger

def get_account(email):
    session = SessionLocal()
    try:
        with session.begin():
            record = session.execute(text("SELECT * FROM account WHERE email = :email"), {'email': email})
            return record.mappings().fetchone()
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to get account {email}: {e}")
        raise
    finally:
        session.close()


def get_account_breaches(email):
    session = SessionLocal()
    try:
        with session.begin():
            account_breaches = session.execute(text("""
                SELECT b.name, b.breach_date, b.data_classes, b.description
                FROM account AS a
                INNER JOIN account_breach AS ab ON a.id = ab.account_id
                INNER JOIN breach AS b ON ab.breach_id = b.id
                WHERE a.email = :email;
            """), {'email': email})
            return [dict(row) for row in account_breaches.mappings().fetchall()] if account_breaches else None
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to get account breaches for {email}: {e}")
        raise
    finally:
        session.close()