"""Manuscript export services.

A registry maps each ``ExportFormat`` to an ``Exporter`` instance that
turns a ``ManuscriptExportBundle`` into bytes/text. To add a new
format (e.g. PDF), implement ``Exporter`` and register it here.
"""

from app.models.enums import ExportFormat
from app.services.exports.base import (
    Exporter,
    ManuscriptExportBundle,
    slugify_for_filename,
)
from app.services.exports.bundle import build_bundle
from app.services.exports.json_export import JSONExporter
from app.services.exports.markdown_export import MarkdownExporter

EXPORTERS: dict[ExportFormat, Exporter] = {
    ExportFormat.MARKDOWN: MarkdownExporter(),
    ExportFormat.JSON: JSONExporter(),
    # ExportFormat.PDF: PDFExporter()  ← register here when implemented.
}


def available_formats() -> list[ExportFormat]:
    return list(EXPORTERS.keys())


__all__ = [
    "EXPORTERS",
    "Exporter",
    "ManuscriptExportBundle",
    "available_formats",
    "build_bundle",
    "slugify_for_filename",
]
