from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.db.models import FileRecord
from app.db.session import get_db

router = APIRouter(prefix="/api/files", tags=["files"])
settings = get_settings()


@router.post("/upload")
async def upload_file(
    session_id: str = "",
    file: UploadFile | None = None,
    db: AsyncSession = Depends(get_db),
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_file_size_mb}MB limit",
        )

    file_id = str(uuid.uuid4())
    ext = Path(file.filename or "unknown").suffix if file.filename else ""
    storage_name = f"{file_id}{ext}"
    storage_path = Path(settings.file_storage_path) / storage_name
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_bytes(content)

    record = FileRecord(
        id=file_id,
        session_id=session_id or None,
        filename=storage_name,
        original_name=file.filename or "unknown",
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        storage_path=str(storage_path),
    )
    db.add(record)
    await db.flush()

    return {
        "id": file_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "mime_type": file.content_type,
    }


@router.get("/{session_id}")
async def list_files(session_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    result = await db.execute(
        select(FileRecord).where(
            (FileRecord.session_id == session_id) | (FileRecord.session_id.is_(None))
        ).order_by(FileRecord.created_at.desc())
    )
    files = result.scalars().all()

    return {
        "files": [
            {
                "id": f.id,
                "original_name": f.original_name,
                "mime_type": f.mime_type,
                "size_bytes": f.size_bytes,
                "created_at": f.created_at.isoformat(),
            }
            for f in files
        ]
    }
