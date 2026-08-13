from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# Schemas describe the shape of data going in and out of the API.
# FastAPI uses them to validate requests automatically and to build the
# Swagger UI documentation, so bad data is rejected before it reaches our code.


# ---------------------------------------------------------------------------
# Users and authentication
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    # What the client must send to /register.
    # EmailStr rejects anything that is not a valid email address.
    email: EmailStr
    password: str

class EmployeeCreate(BaseModel):
    # What a manager sends when creating an employee account.
    email: EmailStr
    password: str


class UserOut(BaseModel):
    # What we send back about a user. Notice there is no password field here,
    # so a password hash can never accidentally be returned in a response.
    id: int
    email: str
    role: str

    class Config:
        # Lets Pydantic read values from a SQLAlchemy object rather than a
        # plain dictionary. Without this, returning a User row would fail.
        # This must be spelled "Config" with a capital C or it is ignored.
        from_attributes = True


class LoginRequest(BaseModel):
    # What the client sends to /login.
    email: EmailStr
    password: str


class Token(BaseModel):
    # What /login sends back. token_type is normally "bearer", which tells the
    # client to send the token as: Authorization: Bearer <token>
    access_token: str
    token_type: str


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    # What a manager sends when creating a task.
    # meeting_id and title are required. The other fields have defaults or
    # can be omitted when they are not needed.
    meeting_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Literal["low", "medium", "high"] = "medium"

    # Multiple employees can be assigned to the same task.
    assigned_user_ids: List[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    # Every field is optional because an update may change only one part of
    # a task. main.py applies only the values included in the request.
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[
        Literal["pending", "in_progress", "completed", "cancelled"]
    ] = None
    priority: Optional[Literal["low", "medium", "high"]] = None

    # Managers can replace the assignment list when required.
    assigned_user_ids: Optional[List[int]] = None

    # Used when recording employee progress in TaskUpdate.
    progress_percentage: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )
    comment: Optional[str] = None


class TaskOut(BaseModel):
    # The shape of a task returned by the API. response_model in main.py
    # ensures only these intended task fields are returned to the client.
    id: int
    meeting_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    status: str
    priority: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    assigned_user_ids: List[int] = Field(default_factory=list)
