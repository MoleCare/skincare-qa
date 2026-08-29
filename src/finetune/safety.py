"""Run every skincare completion through MoleCare's skin-care-harness."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from finetune.paths import HARNESS_PYTHON


@dataclass(frozen=True)
class GuardHit:
    index: int
    user: str
    verdict: str
    rules: tuple[str, ...]
    excerpt: str


def _load_guard():
    if not HARNESS_PYTHON.is_dir():
        raise FileNotFoundError(
            f"skin-care-harness Python package not found at {HARNESS_PYTHON}. "
            "Clone MoleCare/skin-care-harness next to molecare-mcp."
        )
    root = str(HARNESS_PYTHON)
    if root not in sys.path:
        sys.path.insert(0, root)
    from skin_care_harness import SkinGuard

    return SkinGuard.with_core_rules()


def review_pairs(pairs: list[tuple[str, str]]) -> list[GuardHit]:
    guard = _load_guard()
    hits: list[GuardHit] = []
    for index, (user, assistant) in enumerate(pairs):
        report = guard.review(assistant)
        if report.verdict == "pass":
            continue
        hits.append(
            GuardHit(
                index=index,
                user=user,
                verdict=report.verdict,
                rules=tuple(f.rule_id for f in report.findings),
                excerpt=(report.findings[0].excerpt or "") if report.findings else "",
            )
        )
    return hits


def assert_safe(pairs: list[tuple[str, str]]) -> None:
    hits = review_pairs(pairs)
    blocks = [h for h in hits if h.verdict == "block"]
    if not blocks:
        return
    lines = [
        f"skin-care-harness blocked {len(blocks)} training answer(s):",
    ]
    for hit in blocks[:8]:
        lines.append(f"  [{hit.index}] {hit.rules} :: {hit.user!r} :: {hit.excerpt!r}")
    raise SystemExit("\n".join(lines))
