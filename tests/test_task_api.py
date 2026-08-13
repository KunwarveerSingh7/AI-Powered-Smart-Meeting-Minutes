from pathlib import Path
import sys
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

import main
import models
from database import Base


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        Base.metadata.create_all(bind=self.engine)

        db = self.SessionLocal()

        manager = models.User(
            email="manager@example.com",
            hashed_password="test-hash",
            role="manager",
        )

        employee_one = models.User(
            email="employee1@example.com",
            hashed_password="test-hash",
            role="employee",
        )

        employee_two = models.User(
            email="employee2@example.com",
            hashed_password="test-hash",
            role="employee",
        )

        db.add_all([manager, employee_one, employee_two])
        db.flush()

        meeting = models.Meeting(
            title="API Test Meeting",
            uploaded_by=manager.id,
            original_filename="meeting.txt",
            stored_file_path="uploads/meeting.txt",
            file_type="txt",
            raw_text="Test meeting content",
            status="draft",
        )

        db.add(meeting)
        db.commit()

        self.manager_id = manager.id
        self.employee_one_id = employee_one.id
        self.employee_two_id = employee_two.id
        self.meeting_id = meeting.id

        db.close()

        self.current_user = {
            "email": "manager@example.com",
            "role": "manager",
        }

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        def override_current_user():
            return self.current_user

        main.app.dependency_overrides[
            main.get_db
        ] = override_get_db

        main.app.dependency_overrides[
            main.get_current_user
        ] = override_current_user

        self.client = TestClient(main.app)

    def tearDown(self):
        self.client.close()
        main.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def create_task_as_manager(self):
        return self.client.post(
            "/tasks",
            json={
                "meeting_id": self.meeting_id,
                "title": "Complete project testing",
                "description": "Test the integrated task API",
                "priority": "high",
                "assigned_user_ids": [
                    self.employee_one_id,
                    self.employee_two_id,
                ],
            },
        )

    def test_manager_can_create_task_with_multiple_assignments(self):
        response = self.create_task_as_manager()

        self.assertEqual(response.status_code, 201)

        data = response.json()

        self.assertEqual(data["meeting_id"], self.meeting_id)
        self.assertEqual(data["created_by"], self.manager_id)
        self.assertEqual(
            set(data["assigned_user_ids"]),
            {
                self.employee_one_id,
                self.employee_two_id,
            },
        )

    def test_employee_cannot_create_task(self):
        self.current_user = {
            "email": "employee1@example.com",
            "role": "employee",
        }

        response = self.client.post(
            "/tasks",
            json={
                "meeting_id": self.meeting_id,
                "title": "Unauthorized task",
                "assigned_user_ids": [],
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_assigned_employee_can_update_progress(self):
        create_response = self.create_task_as_manager()
        task_id = create_response.json()["id"]

        self.current_user = {
            "email": "employee1@example.com",
            "role": "employee",
        }

        response = self.client.put(
            f"/tasks/{task_id}",
            json={
                "status": "in_progress",
                "progress_percentage": 40,
                "comment": "Work has started",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["status"],
            "in_progress",
        )

        db = self.SessionLocal()

        update = (
            db.query(models.TaskUpdate)
            .filter(models.TaskUpdate.task_id == task_id)
            .one()
        )

        self.assertEqual(
            update.updated_by,
            self.employee_one_id,
        )
        self.assertEqual(update.progress_percentage, 40)
        self.assertEqual(update.comment, "Work has started")

        db.close()

    def test_unassigned_employee_cannot_edit_task(self):
        response = self.client.post(
            "/tasks",
            json={
                "meeting_id": self.meeting_id,
                "title": "Employee one task",
                "assigned_user_ids": [
                    self.employee_one_id
                ],
            },
        )

        task_id = response.json()["id"]

        self.current_user = {
            "email": "employee2@example.com",
            "role": "employee",
        }

        response = self.client.put(
            f"/tasks/{task_id}",
            json={
                "status": "completed",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_change_task_details(self):
        response = self.create_task_as_manager()
        task_id = response.json()["id"]

        self.current_user = {
            "email": "employee1@example.com",
            "role": "employee",
        }

        response = self.client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Changed by employee",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_can_replace_assignments(self):
        response = self.create_task_as_manager()
        task_id = response.json()["id"]

        response = self.client.put(
            f"/tasks/{task_id}",
            json={
                "assigned_user_ids": [
                    self.employee_one_id
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["assigned_user_ids"],
            [self.employee_one_id],
        )


if __name__ == "__main__":
    unittest.main()
