from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import schemas
from auth_utils import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


Base.metadata.create_all(bind=engine)

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)

templates = Jinja2Templates(
    directory=str(FRONTEND_DIR),
)


@app.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="basic.html",
    )

# this decides the route for user from login page to the dashboard

# route to manager dashboard
@app.get("/manager-dashboard")
def manager_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="manager_dashboard.html",
    )


# route to employee dashboard
@app.get("/employee-dashboard")
def employee_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="employee_dashboard.html",
    )


@app.get("/")
def read_root():
    return {"message": "Backend is running"}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@app.post("/register", response_model=schemas.UserOut)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="employee",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=schemas.Token)
def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == credentials.email)
        .first()
    )

    if not user or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/me")
def read_current_user(
    current_user: dict = Depends(get_current_user),
):
    return current_user

# Create Employee
@app.post("/employees", response_model=schemas.UserOut)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only managers are allowed to create employee accounts.
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can create employee accounts"
        )

    # Check if an account with this email already exists.
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == employee.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create the employee account.
    new_employee = models.User(
        email=employee.email,
        hashed_password=hash_password(employee.password),
        role="employee"
    )

    # Save the employee to the database.
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee

@app.get("/employees", response_model=List[schemas.UserOut])
def get_employees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can view employees"
        )

    employees = (
        db.query(models.User)
        .filter(models.User.role == "employee")
        .all()
    )

    return employees


# ---------------------------------------------------------------------------
# Task helpers
# ---------------------------------------------------------------------------

def _get_database_user(
    db: Session,
    current_user: dict,
) -> models.User:
    email = current_user.get("email")

    user = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user was not found",
        )

    return user


def _get_task_or_404(
    db: Session,
    task_id: int,
) -> models.Task:
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


def _validate_assigned_users(
    db: Session,
    user_ids: list[int],
) -> list[int]:
    # Remove duplicate IDs while preserving their original order.
    unique_ids = list(dict.fromkeys(user_ids))

    if not unique_ids:
        return []

    users = (
        db.query(models.User)
        .filter(models.User.id.in_(unique_ids))
        .all()
    )

    found_ids = {user.id for user in users}
    missing_ids = [
        user_id
        for user_id in unique_ids
        if user_id not in found_ids
    ]

    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail=(
                "Assigned user IDs do not exist: "
                + ", ".join(str(user_id) for user_id in missing_ids)
            ),
        )

    return unique_ids


def _task_to_response(task: models.Task) -> dict:
    return {
        "id": task.id,
        "meeting_id": task.meeting_id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "status": task.status,
        "priority": task.priority,
        "created_by": task.created_by,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assigned_user_ids": [
            assignment.user_id
            for assignment in task.assignments
        ],
    }
# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@app.post(
    "/tasks",
    response_model=schemas.TaskOut,
    status_code=201,
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    creator = _get_database_user(db, current_user)

    if creator.role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can create tasks",
        )

    meeting = (
        db.query(models.Meeting)
        .filter(models.Meeting.id == task.meeting_id)
        .first()
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    assigned_user_ids = _validate_assigned_users(
        db,
        task.assigned_user_ids,
    )

    new_task = models.Task(
        meeting_id=task.meeting_id,
        created_by=creator.id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        status="pending",
    )

    for user_id in assigned_user_ids:
        new_task.assignments.append(
            models.TaskAssignment(user_id=user_id)
        )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Task could not be created",
        ) from exc

    return _task_to_response(new_task)


@app.get(
    "/tasks",
    response_model=list[schemas.TaskOut],
)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_database_user(db, current_user)

    if user.role == "manager":
        tasks = db.query(models.Task).all()
    else:
        tasks = (
            db.query(models.Task)
            .join(models.TaskAssignment)
            .filter(models.TaskAssignment.user_id == user.id)
            .distinct()
            .all()
        )

    return [
        _task_to_response(task)
        for task in tasks
    ]


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut,
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_database_user(db, current_user)
    task = _get_task_or_404(db, task_id)

    if user.role != "manager":
        is_assigned = any(
            assignment.user_id == user.id
            for assignment in task.assignments
        )

        if not is_assigned:
            raise HTTPException(
                status_code=403,
                detail="Not allowed to view this task",
            )

    return _task_to_response(task)


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut,
)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_database_user(db, current_user)
    task = _get_task_or_404(db, task_id)

    update_data = task_update.model_dump(exclude_unset=True)
    fields_requested = task_update.model_fields_set

    assignment_change_requested = (
        "assigned_user_ids" in fields_requested
    )
    progress_requested = (
        "progress_percentage" in fields_requested
    )
    comment_requested = "comment" in fields_requested

    assigned_user_ids = update_data.pop(
        "assigned_user_ids",
        None,
    )
    progress_percentage = update_data.pop(
        "progress_percentage",
        None,
    )
    comment = update_data.pop(
        "comment",
        None,
    )

    if user.role != "manager":
        is_assigned = any(
            assignment.user_id == user.id
            for assignment in task.assignments
        )

        if not is_assigned:
            raise HTTPException(
                status_code=403,
                detail="Not allowed to edit this task",
            )

        # Employees may update their task status/progress/comment,
        # but cannot change task details or assignments.
        disallowed_fields = set(update_data) - {"status"}

        if disallowed_fields or assignment_change_requested:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Employees can only update task "
                    "status, progress and comments"
                ),
            )

    if user.role == "manager" and assignment_change_requested:
        validated_ids = _validate_assigned_users(
            db,
            assigned_user_ids or [],
        )

        # Reuse existing assignment rows where possible so the
        # task_id/user_id unique constraint is not violated.
        existing_assignments = {
            assignment.user_id: assignment
            for assignment in task.assignments
        }

        task.assignments = [
            existing_assignments.get(user_id)
            or models.TaskAssignment(user_id=user_id)
            for user_id in validated_ids
        ]

    for field, value in update_data.items():
        if field in {"title", "status", "priority"} and value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

        setattr(task, field, value)

    if (
        "status" in fields_requested
        or progress_requested
        or comment_requested
    ):
        task.updates.append(
            models.TaskUpdate(
                updated_by=user.id,
                status=task.status,
                progress_percentage=(
                    progress_percentage
                    if progress_percentage is not None
                    else 0
                ),
                comment=comment,
            )
        )

    try:
        db.commit()
        db.refresh(task)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Task could not be updated",
        ) from exc

    return _task_to_response(task)


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_database_user(db, current_user)

    if user.role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can delete tasks",
        )

    task = _get_task_or_404(db, task_id)

    try:
        db.delete(task)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Task could not be deleted",
        ) from exc

    return {"message": "Task deleted"}
