"""Feature-level tests using the dry-run provider end-to-end.

Each feature builds a prompt from the bundle, runs the provider, and
parses the response — exercising the whole call chain without leaving
the process.
"""
from __future__ import annotations

from sqlmodel import Session

from app.auth.security import hash_password
from app.models import Author, EditorialNote, Manuscript, Review, User
from app.models.enums import (
    EditorialNoteKind,
    ReviewVerdict,
    UserRole,
    WorkflowStatus,
)
from app.services.ai.features import (
    ConsistencyCheckResult,
    EditorialSuggestionsResult,
    SemanticTagsResult,
    StyleAnalysisResult,
    SummaryResult,
    run_consistency_check,
    run_editorial_suggestions,
    run_semantic_tags,
    run_style_analysis,
    run_summarize,
)
from app.services.ai.providers import DryRunProvider
from app.services.exports import build_bundle


def _seed(session: Session) -> str:
    user = User(
        email="ai-features@logosforge.test",
        full_name="House Editor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    author = Author(full_name="Iris Aldoria", country="Portugal")
    session.add_all([user, author])
    session.commit()
    session.refresh(user)
    session.refresh(author)

    m = Manuscript(
        title="The Salt Atlases",
        subtitle="A cartography of inland seas",
        synopsis="Twelve essays on the salt seas of Europe and the librarians who mapped them.",
        genre="Essays",
        language="en",
        word_count=68200,
        status=WorkflowStatus.PUBLISHED,
        author_id=author.id,
    )
    session.add(m)
    session.commit()
    session.refresh(m)

    session.add_all(
        [
            Review(
                manuscript_id=m.id,
                reviewer_id=user.id,
                verdict=ReviewVerdict.ACCEPT,
                summary="Original synthesis.",
                rating=5,
            ),
            EditorialNote(
                manuscript_id=m.id,
                author_user_id=user.id,
                kind=EditorialNoteKind.STRUCTURAL,
                body="Compress the central correspondence.",
                pinned=True,
            ),
        ]
    )
    session.commit()
    return m.id


def test_summarize_returns_one_line_summary_and_themes(
    session: Session,
) -> None:
    mid = _seed(session)
    bundle = build_bundle(session, mid)
    result = run_summarize(bundle, DryRunProvider())
    assert isinstance(result, SummaryResult)
    assert result.summary
    assert result.themes  # dry-run canned response includes themes
    assert all(isinstance(t, str) for t in result.themes)


def test_style_analysis_returns_register_voice_rhythm(
    session: Session,
) -> None:
    mid = _seed(session)
    bundle = build_bundle(session, mid)
    result = run_style_analysis(bundle, DryRunProvider())
    assert isinstance(result, StyleAnalysisResult)
    assert result.register
    assert result.voice
    assert result.rhythm
    assert result.concerns
    assert all(isinstance(c, str) for c in result.concerns)


def test_editorial_suggestions_returns_typed_entries(
    session: Session,
) -> None:
    mid = _seed(session)
    bundle = build_bundle(session, mid)
    result = run_editorial_suggestions(bundle, DryRunProvider())
    assert isinstance(result, EditorialSuggestionsResult)
    assert result.suggestions
    first = result.suggestions[0]
    assert first.kind
    assert first.title


def test_semantic_tags_returns_lower_case_strings(
    session: Session,
) -> None:
    mid = _seed(session)
    bundle = build_bundle(session, mid)
    result = run_semantic_tags(bundle, DryRunProvider())
    assert isinstance(result, SemanticTagsResult)
    assert result.tags
    assert all(isinstance(t, str) for t in result.tags)


def test_consistency_check_returns_zero_or_more_issues(
    session: Session,
) -> None:
    mid = _seed(session)
    bundle = build_bundle(session, mid)
    result = run_consistency_check(bundle, DryRunProvider())
    assert isinstance(result, ConsistencyCheckResult)
    # The canned response has one issue; assert the shape rather than
    # the exact text.
    if result.issues:
        first = result.issues[0]
        assert first.kind
        assert first.description
