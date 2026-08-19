# TODO: Decide final account registration method.
# Option 1: Only managers can create employee accounts.
# Option 2: Allow employees to sign up for their own accounts.


#Sources
#Source 1: https://fastapi.tiangolo.com/tutorial/first-steps/
#Source 2: https://docs.sqlalchemy.org/en/21/orm/session_basics.html#framing-out-a-begin-commit-rollback-block
#Source 3: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
#Source 4: https://fastapi.tiangolo.com/advanced/templates/
#Source 5: https://github.com/pydantic/pydantic/blob/main/docs/concepts/models.md
#Source 6: https://fastapi.tiangolo.com/tutorial/request-forms/
#Source 7: https://docs.sqlalchemy.org/en/20/orm/session_basics.html



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
 
 
# authentication
 
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = (
        db.query(models.User)
        .filter(
            models.User.email == current_user["email"]
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "position": user.position,
    }
 
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
    role="employee",
    name=employee.name,
    position=employee.position
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
 
 
# task helpers
 
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
 
 
# meeting upload
 
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
    "original_filename": meeting.original_filename,
    "file_type": meeting.file_type,
    "raw_text": meeting.raw_text,

    # AI-generated summary saved during Stage 4.5
    "ai_summary": meeting.ai_summary,

    "status": meeting.status,

    # Send all decisions belonging to this meeting
    "decisions": [
        {
            "id": decision.id,
            "decision_text": decision.decision_text
        }
        for decision in meeting.decisions
    ],

    # Send all AI-generated tasks connected to this meeting
    "tasks": [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "priority": task.priority,
            "status": task.status,

            # This will normally be empty at this stage because
            # the manager has not confirmed employee assignments yet.
            "assigned_user_ids": [
                assignment.user_id
                for assignment in task.assignments
            ]
        }
        for task in meeting.tasks
    ]
}

@app.put("/meetings/{meeting_id}/summary")
def update_meeting_summary(
    meeting_id: int,
    summary_update: schemas.MeetingSummaryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only managers can edit the AI-generated meeting summary.
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can edit meeting summaries"
        )

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

    meeting.ai_summary = summary_update.ai_summary

    try:
        db.commit()
        db.refresh(meeting)

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Meeting summary could not be updated"
        ) from error

    return {
        "message": "Meeting summary updated",
        "ai_summary": meeting.ai_summary
    }


@app.put("/decisions/{decision_id}")
def update_decision(
    decision_id: int,
    decision_update: schemas.DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only managers can edit decisions extracted by the AI.
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can edit decisions"
        )

    decision = (
        db.query(models.Decision)
        .filter(models.Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    decision.decision_text = decision_update.decision_text

    try:
        db.commit()
        db.refresh(decision)

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Decision could not be updated"
        ) from error

    return {
        "message": "Decision updated",
        "id": decision.id,
        "decision_text": decision.decision_text
    }


# publish review meeting

@app.put("/meetings/{meeting_id}/publish")
def publish_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Only managers can publish meetings",
        )

    meeting = (
        db.query(models.Meeting)
        .filter(models.Meeting.id == meeting_id)
        .first()
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    if not meeting.ai_summary:
        raise HTTPException(
            status_code=400,
            detail="Meeting must be analysed before publishing",
        )

    meeting.status = "published"
    meeting.published_at = datetime.now()

    try:
        db.commit()
        db.refresh(meeting)

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Meeting could not be published",
        ) from error

    return {
        "message": "Meeting published successfully",
        "meeting_id": meeting.id,
        "status": meeting.status,
        "published_at": meeting.published_at,
    }


@app.get("/manager/meetings")
def get_manager_meetings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Manager access only",
        )

    meetings = (
        db.query(models.Meeting)
        .order_by(models.Meeting.id.desc())
        .all()
    )

    return [
        {
            "id": meeting.id,
            "title": meeting.title,
            "meeting_date": meeting.meeting_date,
            "original_filename": meeting.original_filename,
            "raw_text": meeting.raw_text,
            "ai_summary": meeting.ai_summary,
            "status": meeting.status,
            "published_at": meeting.published_at,
            "decisions": [
                {
                    "id": decision.id,
                    "decision_text": decision.decision_text,
                }
                for decision in meeting.decisions
            ],
        }
        for meeting in meetings
    ]

@app.get("/employee/meetings")
def get_employee_meetings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Only employees can use this endpoint.
    if current_user["role"] != "employee":
        raise HTTPException(
            status_code=403,
            detail="Employee access only",
        )

    employee = (
        db.query(models.User)
        .filter(
            models.User.email ==
            current_user["email"]
        )
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    # Find published meetings where this employee
    # has at least one assigned task.
    meetings = (
        db.query(models.Meeting)
        .join(
            models.Task,
            models.Task.meeting_id ==
            models.Meeting.id,
        )
        .join(
            models.TaskAssignment,
            models.TaskAssignment.task_id ==
            models.Task.id,
        )
        .filter(
            models.TaskAssignment.user_id ==
            employee.id,

            models.Meeting.status ==
            "published",
        )
        .distinct()
        .order_by(
            models.Meeting.id.desc()
        )
        .all()
    )

    return [
        {
            "id": meeting.id,
            "title": meeting.title,
            "meeting_date":
                meeting.meeting_date,
            "status": meeting.status,
            "published_at":
                meeting.published_at,
                "raw_text": meeting.raw_text,

            "ai_summary":
                meeting.ai_summary,

            "decisions": [
                {
                    "id": decision.id,
                    "decision_text":
                        decision.decision_text,
                }
                for decision
                in meeting.decisions
            ],
        }
        for meeting in meetings
    ]


@app.get("/manager/analytics")
def get_manager_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Manager access only",
        )

    now = datetime.now()

    # -------------------------
    # Meeting statistics
    # -------------------------

    total_meetings = (
        db.query(models.Meeting)
        .count()
    )

    draft_meetings = (
        db.query(models.Meeting)
        .filter(
            models.Meeting.status == "draft"
        )
        .count()
    )

    published_meetings = (
        db.query(models.Meeting)
        .filter(
            models.Meeting.status == "published"
        )
        .count()
    )

    # task statisitcs

    total_tasks = (
        db.query(models.Task)
        .count()
    )

    pending_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.status == "pending"
        )
        .count()
    )

    in_progress_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.status == "in_progress"
        )
        .count()
    )

    completed_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.status == "completed"
        )
        .count()
    )

    cancelled_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.status == "cancelled"
        )
        .count()
    )

    overdue_tasks = (
        db.query(models.Task)
        .filter(
            models.Task.due_date.isnot(None),
            models.Task.due_date < now,
            models.Task.status.notin_(
                ["completed", "cancelled"]
            ),
        )
        .count()
    )

    # completion percentage

    completion_percentage = 0

    if total_tasks > 0:
        completion_percentage = round(
            (
                completed_tasks /
                total_tasks
            ) * 100,
            1,
        )

    return {
        "meetings": {
            "total": total_meetings,
            "draft": draft_meetings,
            "published": published_meetings,
        },

        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks,
            "cancelled": cancelled_tasks,
            "overdue": overdue_tasks,
        },

        "completion_percentage":
            completion_percentage,
    }


@app.get("/manager/analytics/team")
def get_manager_team_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=403,
            detail="Manager access only",
        )

    now = datetime.now()

    employees = (
        db.query(models.User)
        .filter(models.User.role == "employee")
        .all()
    )

    employee_stats = []

    for employee in employees:

        tasks = (
            db.query(models.Task)
            .join(models.TaskAssignment)
            .filter(
                models.TaskAssignment.user_id == employee.id
            )
            .distinct()
            .all()
        )

        total = len(tasks)

        pending = sum(
            1 for task in tasks
            if task.status == "pending"
        )

        in_progress = sum(
            1 for task in tasks
            if task.status == "in_progress"
        )

        completed = sum(
            1 for task in tasks
            if task.status == "completed"
        )

        overdue = sum(
            1 for task in tasks
            if (
                task.due_date is not None
                and task.due_date < now
                and task.status
                not in {"completed", "cancelled"}
            )
        )

        completion_percentage = 0

        if total > 0:
            completion_percentage = round(
                (completed / total) * 100,
                1,
            )

        employee_stats.append({
            "employee_id": employee.id,
            "email": employee.email,
            "name" : employee.name,
            "position" : employee.position,
            "total_tasks": total,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
            "completion_percentage":
                completion_percentage,
        })


    # prioty if taskd

    high_priority = (
        db.query(models.Task)
        .filter(
            models.Task.priority == "high"
        )
        .count()
    )

    medium_priority = (
        db.query(models.Task)
        .filter(
            models.Task.priority == "medium"
        )
        .count()
    )

    low_priority = (
        db.query(models.Task)
        .filter(
            models.Task.priority == "low"
        )
        .count()
    )


    # most completed tasks

    top_employee = None

    if employee_stats:
        top_employee = max(
            employee_stats,
            key=lambda employee:
                employee["completed_tasks"],
        )

    return {
        "employees": employee_stats,

        "priority_breakdown": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority,
        },

        "top_employee": top_employee,
    }


@app.get("/employee/analytics")
def get_employee_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Only employees can access personal analytics.
    if current_user["role"] != "employee":
        raise HTTPException(
            status_code=403,
            detail="Employee access only",
        )

    # Find the logged-in employee.
    employee = (
        db.query(models.User)
        .filter(
            models.User.email ==
            current_user["email"]
        )
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee account not found",
        )

    now = datetime.now()

    # Get every task assigned to this employee.
    assigned_tasks = (
        db.query(models.Task)
        .join(models.TaskAssignment)
        .filter(
            models.TaskAssignment.user_id ==
            employee.id
        )
        .all()
    )

    total_tasks = len(assigned_tasks)

    pending_tasks = sum(
        1
        for task in assigned_tasks
        if task.status == "pending"
    )

    in_progress_tasks = sum(
        1
        for task in assigned_tasks
        if task.status == "in_progress"
    )

    completed_tasks = sum(
        1
        for task in assigned_tasks
        if task.status == "completed"
    )

    overdue_tasks = sum(
        1
        for task in assigned_tasks
        if (
            task.due_date is not None
            and task.due_date < now
            and task.status
            not in {"completed", "cancelled"}
        )
    )

    completion_percentage = 0

    if total_tasks > 0:
        completion_percentage = round(
            (
                completed_tasks /
                total_tasks
            ) * 100,
            1,
        )

    return {
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_percentage":
            completion_percentage,
    }
# employee access to the published meetings

@app.get("/employee/meetings/{meeting_id}")
def get_employee_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "employee":
        raise HTTPException(
            status_code=403,
            detail="Employee access only",
        )

    employee = (
        db.query(models.User)
        .filter(
            models.User.email == current_user["email"]
        )
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    meeting = (
        db.query(models.Meeting)
        .filter(models.Meeting.id == meeting_id)
        .first()
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    if meeting.status != "published":
        raise HTTPException(
            status_code=403,
            detail="Meeting has not been published",
        )

    assigned_task = (
        db.query(models.TaskAssignment)
        .join(
            models.Task,
            models.TaskAssignment.task_id == models.Task.id,
        )
        .filter(
            models.Task.meeting_id == meeting_id,
            models.TaskAssignment.user_id == employee.id,
        )
        .first()
    )

    if assigned_task is None:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this meeting",
        )

    return {
        "id": meeting.id,
        "title": meeting.title,
        "meeting_date": meeting.meeting_date,
        "ai_summary": meeting.ai_summary,
        "decisions": [
            {
                "id": decision.id,
                "decision_text": decision.decision_text,
            }
            for decision in meeting.decisions
        ],
    }
 
 
# meeting processing


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

    # run ai anlyiss
    try:
        # Send the extracted meeting text to our AI service.
        
        result = analyse_meeting(meeting.raw_text)

    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error


    # find manageer ind atabase

    # Tasks require a created_by user ID.
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


    # remove previous ai results

    # manager can cluck analysis more thghan once
    #prevent duplicate recssords

    db.query(models.Decision).filter(
        models.Decision.meeting_id == meeting.id
    ).delete()

    # Get previous tasks for this meeting.
    
    existing_tasks = (
    db.query(models.Task)
    .filter(models.Task.meeting_id == meeting.id)
    .all()
    )

    for existing_task in existing_tasks:
        db.delete(existing_task)


    # save ai summary

    # ai_summary already exists as a column in the Meeting model.
    meeting.ai_summary = result.get("summary")


    # save ai decision
    for decision_text in result.get("decisions", []):

        # Ignore null or empty decisions.
        if not decision_text:
            continue

        decision = models.Decision(
            meeting_id=meeting.id,
            decision_text=decision_text
        )

        db.add(decision)


    # save ai tasks

    for item in result.get("action_items", []):

        task_title = item.get("task")

        # Ignore an invalid AI action item with no task title.
        if not task_title:
            continue


        # convert ai deadline

        # Llama returns deadlines as YYYY-MM-DD strings.
      
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


        # preserve ai assigne and note

        description_parts = []

        # manager confirms lter
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


        # create database task

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


    # commit all ai results

    try:
        db.commit()
        db.refresh(meeting)

    except Exception as error:

     
        db.rollback()

        # TEMPORARY DEBUGGING:
     
        print("DATABASE SAVE ERROR:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="AI analysis succeeded but results could not be saved"
        ) from error


    # return successful results

    return {
        "message": "Meeting analysed and AI results saved successfully",
        "meeting_id": meeting.id,
        "analysis": result
    }


# tasks
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
    .filter(
        models.TaskAssignment.user_id == user.id,
        models.Task.status.notin_(
            ["completed", "cancelled"]
        )
    )
    .distinct()
    .all()
)
        
 
    return [
        _task_to_response(task)
        for task in tasks
    ]


@app.get(
    "/tasks/history",
    response_model=list[schemas.TaskOut],
)
def get_task_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_database_user(
        db,
        current_user
    )

    if user.role == "manager":

        tasks = (
            db.query(models.Task)
            .filter(
                models.Task.status.in_(
                    ["completed", "cancelled"]
                )
            )
            .all()
        )

    else:

        tasks = (
            db.query(models.Task)
            .join(models.TaskAssignment)
            .filter(
                models.TaskAssignment.user_id == user.id,
                models.Task.status.in_(
                    ["completed", "cancelled"]
                )
            )
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



@app.get("/tasks/{task_id}/updates")
def get_task_updates(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _get_database_user(
        db,
        current_user
    )

    task = _get_task_or_404(
        db,
        task_id
    )

    # Managers can view any task history.
    # Employees can only view history for tasks
    # that are assigned to them.
    if user.role != "manager":

        is_assigned = any(
            assignment.user_id == user.id
            for assignment in task.assignments
        )

        if not is_assigned:
            raise HTTPException(
                status_code=403,
                detail="Not allowed to view this task history"
            )

    updates = (
        db.query(models.TaskUpdate)
        .filter(
            models.TaskUpdate.task_id == task_id
        )
        .order_by(
            models.TaskUpdate.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": update.id,
            "task_id": update.task_id,
            "updated_by": update.updated_by,
            "status": update.status,
            "progress_percentage":
                update.progress_percentage,
            "comment": update.comment,
            "created_at": update.created_at
        }
        for update in updates
    ]
 
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

    comment_requested = (
        "comment" in fields_requested
    )

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

    # find latest t6ask progress

    latest_update = (
        db.query(models.TaskUpdate)
        .filter(
            models.TaskUpdate.task_id == task.id
        )
        .order_by(
            models.TaskUpdate.created_at.desc(),
            models.TaskUpdate.id.desc(),
        )
        .first()
    )

    current_progress = (
        latest_update.progress_percentage
        if latest_update
        else 0
    )

    requested_status = update_data.get(
        "status",
        task.status,
    )

    # employee permissions and prohgress rules

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

        # Employees cannot reopen a completed task.
        if (
            task.status == "completed"
            and requested_status != "completed"
        ):
            raise HTTPException(
                status_code=400,
                detail="A completed task cannot be reopened",
            )

        # Employees cannot decrease progress.
        if (
            progress_percentage is not None
            and progress_percentage < current_progress
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Progress cannot decrease from "
                    f"{current_progress}%"
                ),
            )

        # Employees may update status, progress and comment only.
        disallowed_fields = (
            set(update_data) - {"status"}
        )

        if (
            disallowed_fields
            or assignment_change_requested
        ):
            raise HTTPException(
                status_code=403,
                detail=(
                    "Employees can only update task "
                    "status, progress and comments"
                ),
            )

    # progrress rule

    # Completed always means 100%.
    if requested_status == "completed":
        progress_percentage = 100

    # Preserve latest progress if no new percentage was supplied.
    effective_progress = (
        progress_percentage
        if progress_percentage is not None
        else current_progress
    )

    # manager assistance changes

    if (
        user.role == "manager"
        and assignment_change_requested
    ):
        validated_ids = _validate_assigned_users(
            db,
            assigned_user_ids or [],
        )

        existing_assignments = {
            assignment.user_id: assignment
            for assignment in task.assignments
        }

        task.assignments = [
            existing_assignments.get(user_id)
            or models.TaskAssignment(
                user_id=user_id
            )
            for user_id in validated_ids
        ]

    # apply normal task field updates

    for field, value in update_data.items():

        if (
            field in {
                "title",
                "status",
                "priority"
            }
            and value is None
        ):
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

        setattr(task, field, value)

    # save task update hisotry

    if (
        "status" in fields_requested
        or progress_requested
        or comment_requested
    ):
        task.updates.append(
            models.TaskUpdate(
                updated_by=user.id,
                status=task.status,
                progress_percentage=
                    effective_progress,
                comment=comment,
            )
        )

    # commit changes

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



 #API endpoints
 # get - login page
 # get - manager dashboard
 # get - employee dashboard
 # get - meeting review
 # get - /
 # post - register
 # post - login
 # get - me
 # post - employees
 # get - employees
 #post - meeting upload
 # get - meeting id
 #put - meeting summary
 # put decision id
 # put - meeting publish
 # get - manager meetings
 # get - employeee meetings
 # get - employee meetind id
 # post - meetng analysidf
 # get - manager analytics
 # get - employees analtycis
 # get - team analytics
 # post - task
 # get - task
 # get - task hisotry
 # get - task id
 # get - task updates
 # put - taks id
 # delete - task id