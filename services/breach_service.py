from sqlalchemy import text
from db import SessionLocal
from config import logger

def upsert_breach(breach):
    session = SessionLocal()
    try:
        with session.begin():
            result = session.execute(text("""
                INSERT INTO breach (
                name, title, domain, breach_date, added_date, modified_date, 
                pwn_count, description, logo_path, data_classes, is_verified,
                is_fabricated, is_sensitive, is_retired, is_spam_list, is_malware, 
                is_subscription_free, is_stealer_log
                )
                VALUES (:name, :title, :domain, :breach_date, :added_date, :modified_date, 
                       :pwn_count, :description, :logo_path, :data_classes, :is_verified, 
                       :is_fabricated, :is_sensitive, :is_retired, :is_spam_list, :is_malware, 
                       :is_subscription_free, :is_stealer_log
                )
                ON CONFLICT (name) DO UPDATE SET
                    title = EXCLUDED.title,
                    domain = EXCLUDED.domain,
                    breach_date = EXCLUDED.breach_date,
                    added_date = EXCLUDED.added_date,
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
                    breach.data_classes IS DISTINCT FROM EXCLUDED.data_classes OR
                    breach.is_verified IS DISTINCT FROM EXCLUDED.is_verified OR
                    breach.is_fabricated IS DISTINCT FROM EXCLUDED.is_fabricated OR
                    breach.is_sensitive IS DISTINCT FROM EXCLUDED.is_sensitive OR
                    breach.is_retired IS DISTINCT FROM EXCLUDED.is_retired OR
                    breach.is_spam_list IS DISTINCT FROM EXCLUDED.is_spam_list OR
                    breach.is_malware IS DISTINCT FROM EXCLUDED.is_malware OR
                    breach.is_subscription_free IS DISTINCT FROM EXCLUDED.is_subscription_free OR
                    breach.is_stealer_log IS DISTINCT FROM EXCLUDED.is_stealer_log
                RETURNING id
            """), {
                'name': breach['Name'],
                'title': breach['Title'],
                'domain': breach['Domain'],
                'breach_date': breach['BreachDate'],
                'added_date': breach['AddedDate'],
                'modified_date': breach['ModifiedDate'],
                'pwn_count': breach['PwnCount'],
                'description': breach['Description'],
                'logo_path': breach['LogoPath'],
                'data_classes': breach['DataClasses'],
                'is_verified': breach['IsVerified'],
                'is_fabricated': breach['IsFabricated'],
                'is_sensitive': breach['IsSensitive'],
                'is_retired': breach['IsRetired'],
                'is_spam_list': breach['IsSpamList'],
                'is_malware': breach['IsMalware'],
                'is_subscription_free': breach['IsSubscriptionFree'],
                'is_stealer_log': breach['IsStealerLog']
            })
            record = result.mappings().fetchone()
            if record:
                return record['id']

            # No row inserted/updated (identical), fetch existing id
            existing = session.execute(
                text("SELECT id FROM breach WHERE name = :name"), {'name': breach['Name']}
            ).mappings().fetchone()

            return existing['id'] if existing else None

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to upsert breach {breach.get('Name')}: {e}")
        raise
    finally:
        session.close()


def upsert_account_breach(account, breach_id):
    session = SessionLocal()
    account_id = account.get('id')

    try:
        with session.begin():
            session.execute(text("""
                                 INSERT INTO account_breach (account_id, breach_id)
                                 VALUES (:account_id, :breach_id) 
                                 ON CONFLICT (account_id, breach_id) DO NOTHING 
                                 """), {"account_id": account_id, "breach_id": breach_id})

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to upsert account breach {account.get('Email')}:{breach_id}: {e}")
    finally:
        session.close()