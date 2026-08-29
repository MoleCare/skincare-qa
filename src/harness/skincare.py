"""Wrap MoleCare skin-care-harness. Do not fork the ruleset."""

from __future__ import annotations

from harness.types import Finding, Outcome


class SkincareGuard:
    def __init__(self) -> None:
        from finetune.safety import _load_guard

        self._guard = _load_guard()

    def check(self, text: str, red_flags: list[str] | None = None) -> Outcome:
        raw = self._guard.check(text, red_flags)
        findings = tuple(
            Finding(f.rule_id, f.severity, (f.excerpt or "")[:80]) for f in raw.findings
        )
        return Outcome(raw.verdict, raw.output, findings, raw.ruleset_version)
