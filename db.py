from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import config

engine = create_engine(config.db_url, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(bind=engine))