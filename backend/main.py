from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
import schemas
from auth_utils import hash_password, verify_password, create_access_token, get_current_user
from typing import List
 
# Creates the database tables from our SQLAlchemy models if they do not exist yet.
Base.metadata.create_all(bind=engine)
 
app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="../frontend"),
    name="static"
)

templates = Jinja2Templates(
    directory="../frontend"
)


@app.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="basic.html"
    )

@app.get("/")
def read_root():
    # Simple health check so we can confirm the server is running.
    return {"message": "Backend is running"}


 
# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
 
@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Stop two accounts being created with the same email address.
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
 
    # The password is hashed before saving. We never store the plain password.
    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="employee"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
 
 
@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
 
    # The same error message is used for a wrong email and a wrong password,
    # so an attacker cannot work out which emails are registered.
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
 
    # The token carries the user's email and role so later requests know who they are.
    token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
 
 
@app.get("/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    # Returns the details of whoever is currently logged in.
    return current_user
 
 
# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
 
@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only managers create tasks. In our system tasks come from meeting
    # documents that a manager uploads and approves, so employees should
    # not be able to create or hand out tasks themselves.
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can create tasks")
 
    # Look up the manager's database record so we can record who created the task.
    creator = db.query(models.User).filter(models.User.email == current_user["email"]).first()
 
    new_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        assigned_to=task.assigned_to,
        created_by=creator.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
 
 
@app.get("/tasks", response_model=List[schemas.TaskOut])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
 
    # Managers see every task. Employees only see the tasks assigned to them.
    if current_user["role"] == "manager":
        return db.query(models.Task).all()
    return db.query(models.Task).filter(models.Task.assigned_to == user.id).all()
 
 
@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Step 1: find the task and make sure it actually exists.
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    # Step 2: check this person is allowed to change this particular task.
    # Without this check any logged-in employee could edit anyone else's task.
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
 
    if current_user["role"] != "manager":
        if task.created_by != user.id and task.assigned_to != user.id:
            raise HTTPException(status_code=403, detail="Not allowed to edit this task")
 
    # Step 3: apply only the fields that were actually sent in the request.
    # exclude_unset=True means missing fields are left unchanged.
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
 
    db.commit()
    db.refresh(task)
    return task
 
 
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Deleting is manager-only, so the role is checked before anything else.
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can delete tasks")
 
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
 
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
 