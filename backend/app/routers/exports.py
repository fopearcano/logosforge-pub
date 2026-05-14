from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session

from app.db import get_session
from app.models.enums import ExportFormat
from app.services.exports import EXPORTERS, build_bundle, slugify_for_filename

router = APIRouter(tags=["exports"])


@router.get(
    "/manuscripts/{manuscript_id}/export",
    summary="Export a manuscript as Markdown or JSON",
)
def export_manuscript(
    manuscript_id: str,
    fmt: ExportFormat = Query(
        default=ExportFormat.MARKDOWN,
        alias="format",
        description="markdown · json · (pdf — pending)",
    ),
    session: Session = Depends(get_session),
) -> Response:
    exporter = EXPORTERS.get(fmt)
    if exporter is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Export format '{fmt.value}' is registered but not yet implemented.",
        )

    bundle = build_bundle(session, manuscript_id)
    body = exporter.render(bundle)
    filename = f"{slugify_for_filename(bundle.manuscript.title)}.{exporter.extension}"
    return Response(
        content=body,
        media_type=exporter.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get(
    "/exports/formats",
    summary="List the export formats this build supports",
    response_model=list[dict],
)
def list_export_formats() -> list[dict]:
    return [
        {
            "format": fmt.value,
            "media_type": exporter.media_type,
            "extension": exporter.extension,
        }
        for fmt, exporter in EXPORTERS.items()
    ]
