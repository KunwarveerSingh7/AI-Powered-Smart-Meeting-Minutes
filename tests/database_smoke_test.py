from pathlib import Path
import sys
from uuid import uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from database import Base
from models import (
    Decision,
    Meeting,
    Task,
    TaskAssignment,
    TaskUpdate,
    User,
)


def run_database_smoke_test():
    """Test the main database models using an isolated temporary database."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestSession()

    test_id = uuid4().hex[:8]
    manager_email = f"manager-{test_id}@example.com"
    employee_email = f"employee-{test_id}@example.com"

    try:
        manager = User(
            email=manager_email,
            hashed_password="test-manager-password-hash",
            role="manager",
        )

        employee = User(
            email=employee_email,
            hashed_password="test-employee-password-hash",
            role="employee",
        )

        db.add_all([manager, employee])
        db.flush()

        meeting = Meeting(
            title="Database Test Meeting",
            uploaded_by=manager.id,
            original_filename="database-test.txt",
            stored_file_path="uploads/database-test.txt",
            file_type="txt",
            raw_text="Discuss and complete the database design.",
            ai_summary="The team reviewed the database design.",
            status="draft",
        )

        db.add(meeting)
        db.flush()

        decision = Decision(
            meeting_id=meeting.id,
            decision_text="Use SQLite with SQLAlchemy ORM.",
        )

        task = Task(
            meeting_id=meeting.id,
            created_by=manager.id,
            title="Complete database testing",
            description="Test all database models and relationships.",
            priority="high",
            status="in_progress",
        )

        db.add_all([decision, task])
        db.flush()

        assignment = TaskAssignment(
            task_id=task.id,
            user_id=employee.id,
        )

        task_update = TaskUpdate(
            task_id=task.id,
            updated_by=employee.id,
            status="in_progress",
            progress_percentage=25,
            comment="Database models have been created.",
        )

        db.add_all([assignment, task_update])
        db.flush()

        meeting_id = meeting.id
        task_id = task.id

        db.expire_all()

        saved_meeting = db.get(Meeting, meeting_id)
        saved_task = db.get(Task, task_id)

        assert saved_meeting is not None
        assert saved_task is not None

        assert saved_meeting.uploader.email == manager_email
        assert len(saved_meeting.decisions) == 1
        assert len(saved_meeting.tasks) == 1

        assert saved_task.creator.email == manager_email

        assert len(saved_task.assignments) == 1
        assert saved_task.assignments[0].user.email == employee_email

        assert len(saved_task.updates) == 1
        assert saved_task.updates[0].progress_percentage == 25

        print("PASS: Users created")
        print("PASS: Meeting created")
        print("PASS: Decision connected to meeting")
        print("PASS: Task connected to meeting")
        print("PASS: Task creator connected to manager")
        print("PASS: Task assigned to employee")
        print("PASS: Task progress update created")
        print("PASS: All database relationships work correctly")

    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        print("Temporary test database removed")


if __name__ == "__main__":
    run_database_smoke_test()
