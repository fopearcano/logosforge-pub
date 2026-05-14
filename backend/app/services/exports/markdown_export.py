from __future__ import annotations

from datetime import datetime, timezone

from app.models.enums import EditorialNoteKind, WorkflowStatus
from app.services.exports.base import Exporter, ManuscriptExportBundle


def _status(status: WorkflowStatus | None) -> str:
    if status is None:
        return "—"
    return status.value.replace("_", " ").title()


def _kind(kind: EditorialNoteKind) -> str:
    return kind.value.replace("_", " ").title()


def _date(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.date().isoformat()


def _verdict(v: str) -> str:
    return v.title()


class MarkdownExporter:
    media_type = "text/markdown; charset=utf-8"
    extension = "md"

    def render(self, bundle: ManuscriptExportBundle) -> bytes:
        m = bundle.manuscript
        a = bundle.author
        lines: list[str] = []

        # — Title block —
        lines.append(f"# {m.title}")
        if m.subtitle:
            lines.append(f"## _{m.subtitle}_")
        lines.append("")
        author_line = a.full_name if a else "Author unknown"
        if a and a.country:
            author_line = f"{author_line} · {a.country}"
        lines.append(f"> {author_line}")
        lines.append("")

        # — Metadata —
        lines.append("## Metadata")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Status | {_status(m.status)} |")
        lines.append(f"| Genre | {m.genre or '—'} |")
        lines.append(f"| Language | {m.language.upper()} |")
        word_count = f"{m.word_count:,}" if m.word_count is not None else "—"
        lines.append(f"| Word count | {word_count} |")
        lines.append(f"| Created | {_date(m.created_at)} |")
        lines.append(f"| Updated | {_date(m.updated_at)} |")
        lines.append(f"| Manuscript ID | `{m.id}` |")
        lines.append("")

        # — Synopsis —
        lines.append("## Synopsis")
        lines.append("")
        lines.append(m.synopsis or "_No synopsis on file._")
        lines.append("")

        # — Workflow chronicle —
        lines.append("## Workflow chronicle")
        lines.append("")
        if not bundle.workflow_events:
            lines.append("_No transitions recorded._")
        else:
            lines.append("| When | From | To | By | Note |")
            lines.append("| --- | --- | --- | --- | --- |")
            for ev in bundle.workflow_events:
                actor = ev.actor.full_name if ev.actor else "system"
                note = (ev.note or "").replace("\n", " ").replace("|", "/")
                lines.append(
                    f"| {_date(ev.created_at)} | "
                    f"{_status(ev.from_status)} | "
                    f"{_status(ev.to_status)} | "
                    f"{actor} | {note} |"
                )
        lines.append("")

        # — Reviews —
        lines.append("## Reviews")
        lines.append("")
        if not bundle.reviews:
            lines.append("_No reviews on file._")
        else:
            for r in bundle.reviews:
                reviewer = r.reviewer.full_name if r.reviewer else "Anonymous"
                rating = f" · {r.rating}/5" if r.rating is not None else ""
                lines.append(
                    f"### {_verdict(r.verdict.value)}{rating} · {reviewer}"
                )
                lines.append(f"_{_date(r.created_at)}_")
                lines.append("")
                lines.append(r.summary)
                lines.append("")

        # — Editorial notes —
        lines.append("## Editorial notes")
        lines.append("")
        if not bundle.editorial_notes:
            lines.append("_No editorial notes on file._")
        else:
            for n in bundle.editorial_notes:
                author_user = n.author_user.full_name if n.author_user else "—"
                pin = " · 📌 Pinned" if n.pinned else ""
                lines.append(f"### {_kind(n.kind)}{pin} · {author_user}")
                lines.append(f"_{_date(n.created_at)}_")
                lines.append("")
                lines.append(n.body)
                lines.append("")

        # — Footer —
        lines.append("---")
        lines.append("")
        exported_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        lines.append(f"_Exported from LOGOSFORGE on {exported_at}._")
        lines.append("")

        return ("\n".join(lines)).encode("utf-8")
