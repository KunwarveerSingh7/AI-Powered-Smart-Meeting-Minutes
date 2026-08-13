from datetime import datetime
from typing import Optional
 
from pydantic import BaseModel, EmailStr
 
 
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
    # What /login sends back. token_type is always "bearer", which tells the
    # client to send the token as: Authorization: Bearer <token>
    access_token: str
    token_type: str
 
 
# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
 
class TaskCreate(BaseModel):
    # What a manager sends when creating a task.
    # Only the title is required. Optional means the field can be left out,
    # and the value after = is used when it is.
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    assigned_to: Optional[int] = None
 
 
class TaskUpdate(BaseModel):
    # Every field is optional here because an update may change just one thing.
    # In main.py, exclude_unset=True means only the fields actually sent are
    # applied, so leaving a field out does not wipe its existing value.
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
 
 
class TaskOut(BaseModel):
    # The shape of a task in our responses. This is what response_model
    # in main.py filters the returned object down to.
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[int]
    created_by: Optional[int]
    created_at: datetime
 
    class Config:
        from_attributes = True
 