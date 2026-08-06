from datetime import datetime
 
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
 
from database import Base
 
 
class User(Base):
    # __tablename__ is the actual name of the table inside the database file.
    __tablename__ = "users"
 
    # primary_key means this is the unique ID for each row. SQLite fills it in
    # automatically, counting up from 1. index=True makes lookups faster.
    id = Column(Integer, primary_key=True, index=True)
 
    # unique=True stops two accounts sharing the same email address.
    # nullable=False means the column cannot be left empty.
    email = Column(String, unique=True, index=True, nullable=False)
 
    # Only the hashed version of the password is stored, never the real one.
    hashed_password = Column(String, nullable=False)
 
    # Controls what the user is allowed to do. New accounts start as employees,
    # and this is the value the permission checks in main.py read.
    role = Column(String, default="employee")  # "manager" or "employee"
 
 
class Task(Base):
    __tablename__ = "tasks"
 
    id = Column(Integer, primary_key=True, index=True)
 
    # The task itself. A title is required, a description is optional.
    title = Column(String, nullable=False)
    description = Column(String)
 
    # default= sets the value used when nothing is supplied on creation.
    status = Column(String, default="pending")   # pending / in_progress / completed
    priority = Column(String, default="medium")  # low / medium / high
 
    # ForeignKey links this column to the id column in the users table, so a
    # task always points at real user records rather than made-up numbers.
    assigned_to = Column(Integer, ForeignKey("users.id"))
 
    # Records which manager created the task. The ownership check in
    # update_task compares against this to decide who may edit the task.
    created_by = Column(Integer, ForeignKey("users.id"))
 
    # Filled in automatically with the time the row was created.
    # datetime.utcnow is passed without brackets on purpose: SQLAlchemy calls
    # it each time a task is added, rather than freezing one startup time.
    created_at = Column(DateTime, default=datetime.utcnow)
 