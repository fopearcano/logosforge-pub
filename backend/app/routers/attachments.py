from __future__ import annotations

from typing import Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import ADMIN_ONLY, AUTHED, get_current_user
from app.db import get_session
from app.models import Attachment, Manuscript, User
from app.models.enums import AttachmentKind
from app.schemas import (
    AttachmentPlaceholderCreate,
    AttachmentRead,
    AttachmentUpdate,
)
from app.services.storage import get_storage, safe_filename
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/attachments", tags=["attachments"])


def _read(attachment: Attachment) -> AttachmentRead:
    return AttachmentRead(
        id=attachment.id,
        created_at=attachment.created_at,
        updated_at=attachment.updated_at,
        manuscript_id=attachment.manuscript_id,
        uploader_id=attachment.uploader_id,
        uploader_name=attachment.uploader.full_name if attachment.uploader else None,
        filename=attachment.filename,
        content_type=attachment.content_type,
        size_bytes=attachment.size_bytes,
        kind=attachment.kind,
        storage_key=attachment.storage_key,
        sha256=attachment.sha256,
        description=attachment.description,
        is_placeholder=attachment.is_placeholder,
    )


@router.get("", response_model=Page[AttachmentRead])
def list_attachments(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
    kind: Optional[AttachmentKind] = Query(default=None),
) -> Page[AttachmentRead]:
    stmt = select(Attachment).options(selectinload(Attachment.uploader))
    if manuscript_id is not None:
        stmt = stmt.where(Attachment.manuscript_id == manuscript_id)
    if kind is not None:
        stmt = stmt.where(Attachment.kind == kind)
    stmt = stmt.order_by(Attachment.created_at.desc())
    items, total = paginate(session, stmt, params)
    return Page[AttachmentRead](
        items=[_read(a) for a in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{attachment_id}", response_model=AttachmentRead)
def get_attachment(
    attachment_id: str, session: Session = Depends(get_session)
) -> AttachmentRead:
    attachment = get_or_404(session, Attachment, attachment_id, name="Attachment")
    return _read(attachment)


@router.post(
    "",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
    summary="Create a placeholder attachment (metadata only, no bytes)",
)
def create_placeholder_attachment(
    payload: AttachmentPlaceholderCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> AttachmentRead:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    attachment = Attachment(
        manuscript_id=payload.manuscript_id,
        uploader_id=user.id,
        filename=payload.filename,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
        kind=payload.kind,
        storage_key=f"placeholder:{uuid4()}",
        description=payload.description,
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return _read(attachment)


@router.post(
    "/upload",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
    summary="Upload a file and record its metadata",
)
def upload_attachment(
    manuscript_id: str = Form(...),
    kind: AttachmentKind = Form(default=AttachmentKind.OTHER),
    description: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> AttachmentRead:
    ensure_exists(session, Manuscript, manuscript_id, name="Manuscript")
    storage = get_storage()
    key = f"attachments/{uuid4()}_{safe_filename(file.filename)}"
    stored = storage.write(key, file.file)

    attachment = Attachment(
        manuscript_id=manuscript_id,
        uploader_id=user.id,
        filename=file.filename or "file",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=stored.size_bytes,
        kind=kind,
        storage_key=stored.storage_key,
        sha256=stored.sha256,
        description=description,
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return _read(attachment)


@router.patch(
    "/{attachment_id}",
    response_model=AttachmentRead,
    dependencies=AUTHED,
)
def update_attachment(
    attachment_id: str,
    payload: AttachmentUpdate,
    session: Session = Depends(get_session),
) -> AttachmentRead:
    attachment = get_or_404(session, Attachment, attachment_id, name="Attachment")
    apply_patch(attachment, payload)
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return _read(attachment)


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=ADMIN_ONLY,
)
def delete_attachment(
    attachment_id: str, session: Session = Depends(get_session)
):
    attachment = get_or_404(session, Attachment, attachment_id, name="Attachment")
    storage = get_storage()
    storage.delete(attachment.storage_key)
    session.delete(attachment)
    session.commit()


@router.get(
    "/{attachment_id}/download",
    summary="Stream the file bytes (404 for placeholder records)",
)
def download_attachment(
    attachment_id: str, session: Session = Depends(get_session)
):
    attachment = get_or_404(session, Attachment, attachment_id, name="Attachment")
    if attachment.is_placeholder:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Placeholder attachment — no file bytes on record.",
        )
    storage = get_storage()
    if not storage.exists(attachment.storage_key):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="File is no longer available on the storage backend.",
        )
    return FileResponse(
        path=storage.path_for(attachment.storage_key),
        filename=attachment.filename,
        media_type=attachment.content_type,
    )
