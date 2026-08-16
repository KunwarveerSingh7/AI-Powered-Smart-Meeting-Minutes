from pathlib import Path
from typing import List
 
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, File, Form
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from file_handler import extract_text
from ai_service import analyse_meeting, check_ollama_running

from database import Base, engine, get_db
import shutil
import models
import schemas
from auth_utils import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
 
from meeting_router import router as meeting_router
 
 
Base.metadata.create_all(bind=engine)
 
app = FastAPI()
 
app.include_router(meeting_router)
 
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
 
@app.get("/meeting-review/{meeting_id}")
def meeting_review_page(
    request: Request,
    meeting_id: int
):
    return templates.TemplateResponse(
        request=request,
        name="meeting_review.html"
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
# Meeting upload
# ---------------------------------------------------------------------------
 
UPLOAD_FOLDER = Path("../upload")
 
UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)
 
 
@app.post("/meetings/upload")
def upload_meeting(
    title: str = Form(...),
    meeting_date: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
 
    # Only managers upload meeting minutes.
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can upload meeting minutes"
        )
 
    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }
 
    extension = Path(file.filename).suffix.lower()
 
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX and TXT files are allowed"
        )
 
    manager = (
        db.query(models.User)
        .filter(
            models.User.email == current_user["email"]
        )
        .first()
    )
 
    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager account not found"
        )
 
    # Add timestamp so two files with the same name
    # do not overwrite each other.
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
 
    safe_filename = (
        timestamp + "_" + Path(file.filename).name
    )
 
    stored_path = (
        UPLOAD_FOLDER / safe_filename
    )
 
    # Save uploaded file.
    with open(stored_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )
 
    # Extract readable text.
    try:
        raw_text = extract_text(stored_path)
 
    except Exception as error:
 
        if stored_path.exists():
            stored_path.unlink()
 
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the uploaded file"
        ) from error
 
    parsed_date = None
 
    if meeting_date:
        try:
            parsed_date = datetime.strptime(
                meeting_date,
                "%Y-%m-%d"
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid meeting date"
            )
 
    meeting = models.Meeting(
        title=title,
        meeting_date=parsed_date,
        uploaded_by=manager.id,
        original_filename=file.filename,
        stored_file_path=str(stored_path),
        file_type=extension.replace(".", ""),
        raw_text=raw_text,
        status="draft"
    )
 
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
 
    return {
        "message": "Meeting uploaded successfully",
        "meeting_id": meeting.id
    }
 
 
@app.get("/meetings/{meeting_id}")
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
 
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can review meetings"
        )
 
    meeting = (
        db.query(models.Meeting)
        .filter(
            models.Meeting.id == meeting_id
        )
        .first()
    )
 
    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )
 
    return {
        "id": meeting.id,
        "title": meeting.title,
        "meeting_date": meeting.meeting_date,
        "original_filename":
            meeting.original_filename,
        "file_type": meeting.file_type,
        "raw_text": meeting.raw_text,
        "status": meeting.status
    }
 
 
# ---------------------------------------------------------------------------
# Meeting Processing
# ---------------------------------------------------------------------------


@app.post("/meetings/{meeting_id}/analyse")
def analyse_meeting_route(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only managers can run AI analysis.
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can analyse meetings"
        )

    # Find the meeting that has already been uploaded.
    meeting = (
        db.query(models.Meeting)
        .filter(models.Meeting.id == meeting_id)
        .first()
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    # AI cannot analyse a meeting if extraction produced no text.
    if not meeting.raw_text:
        raise HTTPException(
            status_code=400,
            detail="Meeting does not contain extracted text"
        )

    # Give a clearer error if Ollama itself is offline.
    if not check_ollama_running():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running"
        )

    # ---------------------------------------------------------------
    # Run AI analysis
    # ---------------------------------------------------------------

    try:
        # Send the extracted meeting text to our AI service.
        # The result contains:
        # summary, decisions, action_items and flags.
        result = analyse_meeting(meeting.raw_text)

    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error


    # ---------------------------------------------------------------
    # Find the manager in the database
    # ---------------------------------------------------------------

    # Tasks require a created_by user ID.
    # The JWT contains the manager's email, so use that email
    # to find the corresponding User database record.
    manager = (
        db.query(models.User)
        .filter(
            models.User.email == current_user["email"]
        )
        .first()
    )

    if manager is None:
        raise HTTPException(
            status_code=404,
            detail="Manager account not found"
        )


    # ---------------------------------------------------------------
    # Remove previous AI results
    # ---------------------------------------------------------------

    # The manager may run the analysis more than once while the
    # meeting is still being reviewed.
    #
    # Delete the previous decisions and tasks for this meeting
    # before storing the newly generated results. This prevents
    # duplicate records.

    db.query(models.Decision).filter(
        models.Decision.meeting_id == meeting.id
    ).delete()

    db.query(models.Task).filter(
        models.Task.meeting_id == meeting.id
    ).delete()


    # ---------------------------------------------------------------
    # Save AI summary
    # ---------------------------------------------------------------

    # ai_summary already exists as a column in the Meeting model.
    meeting.ai_summary = result.get("summary")


    # ---------------------------------------------------------------
    # Save AI decisions
    # ---------------------------------------------------------------

    for decision_text in result.get("decisions", []):

        # Ignore null or empty decisions.
        if not decision_text:
            continue

        decision = models.Decision(
            meeting_id=meeting.id,
            decision_text=decision_text
        )

        db.add(decision)


    # ---------------------------------------------------------------
    # Save AI action items as tasks
    # ---------------------------------------------------------------

    for item in result.get("action_items", []):

        task_title = item.get("task")

        # Ignore an invalid AI action item with no task title.
        if not task_title:
            continue


        # -----------------------------------------------------------
        # Convert AI deadline
        # -----------------------------------------------------------

        # Llama returns deadlines as YYYY-MM-DD strings.
        # SQLAlchemy expects a Python datetime for due_date.
        due_date = None

        deadline = item.get("deadline")

        if deadline:
            try:
                due_date = datetime.strptime(
                    deadline,
                    "%Y-%m-%d"
                )
            except ValueError:
                # If AI somehow returns an invalid date,
                # leave the deadline empty for manager review.
                due_date = None


        # -----------------------------------------------------------
        # Preserve AI assignee and notes
        # -----------------------------------------------------------

        description_parts = []

        # We are NOT automatically assigning an employee account yet.
        # The AI gives us a person's name, while the database assignment
        # system uses user IDs. The manager will confirm this later.
        if item.get("assignee"):
            description_parts.append(
                "AI extracted assignee: "
                + str(item["assignee"])
            )

        if item.get("notes"):
            description_parts.append(
                str(item["notes"])
            )

        description = (
            "\n".join(description_parts)
            if description_parts
            else None
        )


        # -----------------------------------------------------------
        # Create database Task
        # -----------------------------------------------------------

        new_task = models.Task(
            meeting_id=meeting.id,
            created_by=manager.id,
            title=task_title,
            description=description,
            due_date=due_date,
            priority=item.get("priority", "medium"),
            status="pending"
        )

        db.add(new_task)


    # ---------------------------------------------------------------
    # Commit all AI results
    # ---------------------------------------------------------------

    try:
        db.commit()
        db.refresh(meeting)

    except Exception as error:

        # Undo the database transaction if saving failed.
        db.rollback()

        # TEMPORARY DEBUGGING:
        # Print the actual database error in the terminal.
        print("DATABASE SAVE ERROR:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="AI analysis succeeded but results could not be saved"
        ) from error


    # ---------------------------------------------------------------
    # Return successful result
    # ---------------------------------------------------------------

    return {
        "message": "Meeting analysed and AI results saved successfully",
        "meeting_id": meeting.id,
        "analysis": result
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
 