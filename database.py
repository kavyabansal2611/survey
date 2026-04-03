
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
load_dotenv()
import os
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # tests connection before using it
    pool_recycle=300,          # recycles connections every 5 minutes
    pool_size=5,
    max_overflow=10
)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base()
def get_db():
        db=SessionLocal()
        try:
                yield db
        finally:
                db.close()
conn=engine.connect()
conn.commit()
conn.close()
