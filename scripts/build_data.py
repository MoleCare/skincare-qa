#!/usr/bin/env python3
"""Build mlx-lm JSONL splits from MoleCare sources + the python-vibe seed."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finetune.paths import DATA_ROOT  # noqa: E402
from finetune.python_vibe import all_pairs as python_pairs  # noqa: E402
from finetune.safety import assert_safe  # noqa: E402
from finetune.skincare_from_molecare import all_pairs as skincare_pairs  # noqa: E402
from finetune.splits import write_splits  # noqa: E402
from finetune.systems import PYTHON_VIBE_SYSTEM, SKINCARE_SYSTEM  # noqa: E402


def main() -> None:
    skin = skincare_pairs()
    assert_safe(skin)
    py = python_pairs()

    skin_counts = write_splits(skin, SKINCARE_SYSTEM, DATA_ROOT / "skincare-qa")
    py_counts = write_splits(py, PYTHON_VIBE_SYSTEM, DATA_ROOT / "python-vibe")

    print("skincare-qa", skin_counts, "from", len(skin), "pairs")
    print("python-vibe", py_counts, "from", len(py), "pairs")
    print("wrote", DATA_ROOT)


if __name__ == "__main__":
    main()
