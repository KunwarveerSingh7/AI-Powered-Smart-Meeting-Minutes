from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
 
 
# Where the database file lives. SQLite stores the whole database in a single
# file, so no separate database server needs to be installed. The generated
# .db file is excluded from GitHub so each member has their own local copy.
DATABASE_URL = "sqlite:///./database/meeting_tracker.db"
 
# The engine is the actual connection to the database file.
# check_same_thread=False is needed because FastAPI may handle requests on
# different threads, and SQLite blocks that by default.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
 
# A factory that produces database sessions. A session is one conversation
# with the database. autocommit=False means nothing is saved until we call
# db.commit(), so a half-finished operation cannot be written by accident.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Every model class in models.py inherits from Base. That is how SQLAlchemy
# knows which classes represent database tables.
Base = declarative_base()
 
 
def get_db():
    # Routes use Depends(get_db) to receive a database session.
    db = SessionLocal()
    try:
        # yield hands the session to the route and pauses here while it runs.
        yield db
    finally:
        # Once the request finishes the session is always closed, even if the
        # route raised an error. This stops connections being left open.
        db.close()
 