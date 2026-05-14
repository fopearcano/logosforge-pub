"""Editorial AI features.

Each feature follows the same shape so the route layer can dispatch
generically:

* a Pydantic result schema,
* a ``run(bundle, provider) -> result`` function,
* a stable feature key from ``AIFeature``.

A new feature is added by writing one of these and registering it in
``FEATURES``.
"""

from typing import Callable

from app.models.enums import AIFeature
from app.services.ai.features.consistency import (
    ConsistencyCheckResult,
    run_consistency_check,
)
from app.services.ai.features.editorial_suggestions import (
    EditorialSuggestionsResult,
    run_editorial_suggestions,
)
from app.services.ai.features.semantic_tags import (
    SemanticTagsResult,
    run_semantic_tags,
)
from app.services.ai.features.style_analysis import (
    StyleAnalysisResult,
    run_style_analysis,
)
from app.services.ai.features.summarize import SummaryResult, run_summarize


# A simple registry. The route layer asks for a feature by enum value
# and gets a runner that takes (bundle, provider) → result.
FEATURES: dict[AIFeature, Callable] = {
    AIFeature.SUMMARIZE: run_summarize,
    AIFeature.STYLE_ANALYSIS: run_style_analysis,
    AIFeature.EDITORIAL_SUGGESTIONS: run_editorial_suggestions,
    AIFeature.SEMANTIC_TAGS: run_semantic_tags,
    AIFeature.CONSISTENCY_CHECK: run_consistency_check,
}


__all__ = [
    "ConsistencyCheckResult",
    "EditorialSuggestionsResult",
    "FEATURES",
    "SemanticTagsResult",
    "StyleAnalysisResult",
    "SummaryResult",
    "run_consistency_check",
    "run_editorial_suggestions",
    "run_semantic_tags",
    "run_style_analysis",
    "run_summarize",
]
