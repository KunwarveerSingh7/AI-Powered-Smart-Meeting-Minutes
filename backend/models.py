from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="employee")  # manager or employee

    uploaded_meetings = relationship(
        "Meeting",
        back_populates="uploader",
    )

    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by",
    )

    task_assignments = relationship(
        "TaskAssignment",
        back_populates="user",
    )

    task_updates = relationship(
        "TaskUpdate",
        back_populates="user",
    )


class Meeting(Base):
    __tablename__ = "meetings"

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck_meetings_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    meeting_date = Column(DateTime, nullable=True)

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    original_filename = Column(String(255), nullable=False)
    stored_file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=True)

    raw_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    status = Column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    published_at = Column(DateTime, nullable=True)

    uploader = relationship(
        "User",
        back_populates="uploaded_meetings",
    )

    decisions = relationship(
        "Decision",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )

    tasks = relationship(
        "Task",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)

    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False,
        index=True,
    )

    decision_text = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    meeting = relationship(
        "Meeting",
        back_populates="decisions",
    )


class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority",
        ),
        CheckConstraint(
            "status IN "
            "('pending', 'in_progress', 'completed', 'cancelled')",
            name="ck_tasks_status",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False,
        index=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True, index=True)

    priority = Column(
        String(20),
        nullable=False,
        default="medium",
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    meeting = relationship(
        "Meeting",
        back_populates="tasks",
    )

    creator = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[created_by],
    )

    assignments = relationship(
        "TaskAssignment",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    updates = relationship(
        "TaskUpdate",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "user_id",
            name="uq_task_assignment",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    assigned_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    task = relationship(
        "Task",
        back_populates="assignments",
    )

    user = relationship(
        "User",
        back_populates="task_assignments",
    )


class TaskUpdate(Base):
    __tablename__ = "task_updates"

    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('pending', 'in_progress', 'completed', 'cancelled')",
            name="ck_task_updates_status",
        ),
        CheckConstraint(
            "progress_percentage >= 0 "
            "AND progress_percentage <= 100",
            name="ck_task_updates_progress",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
        index=True,
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    status = Column(String(20), nullable=False)

    progress_percentage = Column(
        Integer,
        nullable=False,
        default=0,
    )

    comment = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    task = relationship(
        "Task",
        back_populates="updates",
    )

    user = relationship(
        "User",
        back_populates="task_updates",
    )
