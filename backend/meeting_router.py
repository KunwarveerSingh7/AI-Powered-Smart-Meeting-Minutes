from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from . import models
    from .auth_utils import get_current_user
    from .database import PROJECT_ROOT, get_db
    from .document_processor import (
        DocumentProcessingError,
        EmptyDocumentError,
        UnsupportedFileTypeError,
        extract_text_from_bytes,
    )
except ImportError:
    import models
    from auth_utils import get_current_user
    from database import PROJECT_ROOT, get_db
    from document_processor import (
        DocumentProcessingError,
        EmptyDocumentError,
        UnsupportedFileTypeError,
        extract_text_from_bytes,
    )


router = APIRouter(prefix="/meetings", tags=["Meetings"])

UPLOAD_DIRECTORY = PROJECT_ROOT / "upload" / "meetings"
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class MeetingUploadResponse(BaseModel):
    meeting_id: int
    title: str
    original_filename: str
    file_type: str
    status: str
    extracted_text: str
    created_at: datetime


@router.post(
    "/upload",
    response_model=MeetingUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_meeting_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload a meeting document, extract its text and store its metadata."""

    cleaned_title = title.strip()
    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Meeting title is required.",
        )

    if len(cleaned_title) > 255:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Meeting title must not exceed 255 characters.",
        )

    if current_user.get("role") != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can upload meeting documents.",
        )

    email = current_user.get("email")
    uploader = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )

    if uploader is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user was not found.",
        )

    if uploader.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can upload meeting documents.",
        )

    original_filename = (file.filename or "").strip()
    if not original_filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The uploaded file must have a filename.",
        )

    if len(original_filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The filename must not exceed 255 characters.",
        )

    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file could not be read.",
        ) from exc
    finally:
        await file.close()

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded file must not exceed 10 MB.",
        )

    try:
        extracted_text = extract_text_from_bytes(
            original_filename,
            content,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except EmptyDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    extension = Path(original_filename).suffix.lower()
    stored_filename = f"{uuid4().hex}{extension}"
    stored_path = UPLOAD_DIRECTORY / stored_filename

    try:
        stored_path.write_bytes(content)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The uploaded document could not be saved.",
        ) from exc

    meeting = models.Meeting(
        title=cleaned_title,
        uploaded_by=uploader.id,
        original_filename=original_filename,
        stored_file_path=str(stored_path),
        file_type=extension.lstrip("."),
        raw_text=extracted_text,
        status="draft",
    )

    try:
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
    except Exception as exc:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The meeting record could not be created.",
        ) from exc

    return MeetingUploadResponse(
        meeting_id=meeting.id,
        title=meeting.title,
        original_filename=meeting.original_filename,
        file_type=meeting.file_type,
        status=meeting.status,
        extracted_text=meeting.raw_text,
        created_at=meeting.created_at,
    )
