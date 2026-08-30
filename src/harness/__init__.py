"""Deterministic wrapper around the skincare model.

Same shape as MoleCare skin-care-harness: the model drafts, the harness
decides whether that draft ships. No extra model in the loop.
"""

from harness.run import complete
from harness.skincare import SkincareGuard
from harness.types import Finding, Outcome

__all__ = [
    "SkincareGuard",
    "complete",
    "Finding",
    "Outcome",
]
