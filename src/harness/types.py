from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    excerpt: str


@dataclass(frozen=True)
class Outcome:
    verdict: str
    output: str | None
    findings: tuple[Finding, ...]
    ruleset_version: str
    fallback: bool = False
