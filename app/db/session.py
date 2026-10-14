from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker  , declarative_base , Session
from app.db.config import settings
from typing import Generator

#base and engine for database connection
Base = declarative_base()
engine = create_engine(url=settings.DATABASE_URL , pool_pre_ping=True)

#database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# function to get database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield(db)
    finally:
        db.close()