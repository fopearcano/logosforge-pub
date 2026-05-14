from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.auth import AUTHED
from app.config import settings
from app.db import get_session
from app.models import AIInsight, Manuscript
from app.models.enums import AIFeature
from app.schemas.ai import (
    AIInsightRead,
    AIProviderInfo,
    AIProviderListing,
    AIRunResponse,
)
from app.services.ai import get_provider
from app.services.ai.features import FEATURES
from app.services.ai.providers import KNOWN_PROVIDERS, PROVIDER_DEFAULTS
from app.services.exports import build_bundle
from app.utils import ensure_exists

router = APIRouter(prefix="/ai", tags=["ai"])


def _insight_read(insight: AIInsight) -> AIInsightRead:
    try:
        payload = json.loads(insight.payload)
    except (json.JSONDecodeError, TypeError):
        payload = {}
    return AIInsightRead(
        id=insight.id,
        created_at=insight.created_at,
        updated_at=insight.updated_at,
        manuscript_id=insight.manuscript_id,
        feature=insight.feature,
        provider=insight.provider,
        model=insight.model,
        payload=payload,
    )


def _run_feature(
    session: Session, manuscript_id: str, feature: AIFeature
) -> AIRunResponse:
    ensure_exists(session, Manuscript, manuscript_id, name="Manuscript")
    bundle = build_bundle(session, manuscript_id)
    provider = get_provider()
    runner = FEATURES[feature]
    result = runner(bundle, provider)

    # Build a clean dict for storage + transport.
    payload = result.model_dump()

    # Provider metadata: we record what answered the call so the
    # cached insight is auditable. The model echoed back by the
    # provider may differ from the requested default (e.g. OpenAI
    # versioning), so prefer it when available.
    response_model = getattr(result, "model", None) or settings.ai_model
    if hasattr(provider, "default_model"):
        response_model = provider.default_model or response_model

    # Stash the result. A fresh insert per call keeps history; the
    # latest row is canonical for the listing endpoint.
    insight = AIInsight(
        manuscript_id=manuscript_id,
        feature=feature,
        provider=provider.name,
        model=response_model,
        payload=json.dumps(payload, ensure_ascii=False),
    )
    session.add(insight)
    session.commit()
    session.refresh(insight)

    return AIRunResponse(
        feature=feature,
        provider=provider.name,
        model=insight.model,
        generated_at=insight.created_at,
        insight_id=insight.id,
        result=payload,
    )


# --- feature endpoints ----------------------------------------------------


@router.post(
    "/manuscripts/{manuscript_id}/summarize",
    response_model=AIRunResponse,
    dependencies=AUTHED,
    summary="Generate an editorial summary for a manuscript",
)
def summarize(
    manuscript_id: str, session: Session = Depends(get_session)
) -> AIRunResponse:
    return _run_feature(session, manuscript_id, AIFeature.SUMMARIZE)


@router.post(
    "/manuscripts/{manuscript_id}/style-analysis",
    response_model=AIRunResponse,
    dependencies=AUTHED,
    summary="Sketch a register / voice / rhythm analysis",
)
def style_analysis(
    manuscript_id: str, session: Session = Depends(get_session)
) -> AIRunResponse:
    return _run_feature(session, manuscript_id, AIFeature.STYLE_ANALYSIS)


@router.post(
    "/manuscripts/{manuscript_id}/editorial-suggestions",
    response_model=AIRunResponse,
    dependencies=AUTHED,
    summary="Offer 2–5 editorial suggestions",
)
def editorial_suggestions(
    manuscript_id: str, session: Session = Depends(get_session)
) -> AIRunResponse:
    return _run_feature(session, manuscript_id, AIFeature.EDITORIAL_SUGGESTIONS)


@router.post(
    "/manuscripts/{manuscript_id}/semantic-tags",
    response_model=AIRunResponse,
    dependencies=AUTHED,
    summary="Propose semantic tags suitable for faceted search",
)
def semantic_tags(
    manuscript_id: str, session: Session = Depends(get_session)
) -> AIRunResponse:
    return _run_feature(session, manuscript_id, AIFeature.SEMANTIC_TAGS)


@router.post(
    "/manuscripts/{manuscript_id}/consistency-check",
    response_model=AIRunResponse,
    dependencies=AUTHED,
    summary="Surface potential narrative consistency issues",
)
def consistency_check(
    manuscript_id: str, session: Session = Depends(get_session)
) -> AIRunResponse:
    return _run_feature(session, manuscript_id, AIFeature.CONSISTENCY_CHECK)


# --- read endpoints -------------------------------------------------------


@router.get(
    "/manuscripts/{manuscript_id}/insights",
    response_model=list[AIInsightRead],
    summary="List cached AI insights for a manuscript",
)
def list_insights(
    manuscript_id: str,
    session: Session = Depends(get_session),
    feature: Optional[AIFeature] = Query(default=None),
    limit: int = Query(50, ge=1, le=200),
) -> list[AIInsightRead]:
    ensure_exists(session, Manuscript, manuscript_id, name="Manuscript")
    stmt = select(AIInsight).where(AIInsight.manuscript_id == manuscript_id)
    if feature is not None:
        stmt = stmt.where(AIInsight.feature == feature)
    stmt = stmt.order_by(AIInsight.created_at.desc()).limit(limit)
    return [_insight_read(i) for i in session.exec(stmt).all()]


@router.get(
    "/providers",
    response_model=AIProviderListing,
    summary="Inspect the configured AI backend",
)
def providers() -> AIProviderListing:
    provider = get_provider()
    base_url = (
        getattr(provider, "base_url", None)
        or PROVIDER_DEFAULTS.get(settings.ai_provider)
    )
    info = AIProviderInfo(
        provider=provider.name,
        model=settings.ai_model,
        base_url=base_url,
        is_live=provider.name != "dry_run",
    )
    return AIProviderListing(active=info, known=list(KNOWN_PROVIDERS))


# --- delete one insight ---------------------------------------------------


@router.delete(
    "/insights/{insight_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=AUTHED,
)
def delete_insight(
    insight_id: str, session: Session = Depends(get_session)
):
    insight = session.get(AIInsight, insight_id)
    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AIInsight not found",
        )
    session.delete(insight)
    session.commit()
