#!/usr/bin/env python3
"""Build mlx-lm JSONL splits from MoleCare skincare sources."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finetune.paths import DATA_ROOT  # noqa: E402
from finetune.safety import assert_safe  # noqa: E402
from finetune.skincare_from_molecare import all_pairs as skincare_pairs  # noqa: E402
from finetune.splits import write_splits  # noqa: E402
from finetune.systems import SKINCARE_SYSTEM  # noqa: E402


def main() -> None:
    skin = skincare_pairs()
    assert_safe(skin)

    skin_counts = write_splits(skin, SKINCARE_SYSTEM, DATA_ROOT / "skincare-qa")

    print("skincare-qa", skin_counts, "from", len(skin), "pairs")
    print("wrote", DATA_ROOT)


if __name__ == "__main__":
    main()
