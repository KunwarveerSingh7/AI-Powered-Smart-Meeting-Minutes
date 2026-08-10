from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Users and authentication
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    meeting_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Literal["low", "medium", "high"] = "medium"

    # Multiple employees can be assigned to the same task.
    assigned_user_ids: List[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
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
