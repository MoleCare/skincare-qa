"""Turn (user, assistant) pairs into mlx-lm chat JSONL splits."""

from __future__ import annotations

import json
import random
from pathlib import Path


def chat_row(system: str, user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def write_splits(
    pairs: list[tuple[str, str]],
    system: str,
    dest: Path,
    *,
    seed: int = 7,
    valid_frac: float = 0.12,
    test_frac: float = 0.12,
) -> dict[str, int]:
    if len(pairs) < 12:
        raise ValueError(f"need at least 12 pairs, got {len(pairs)}")

    rng = random.Random(seed)
    shuffled = list(pairs)
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_test = max(2, int(n * test_frac))
    n_valid = max(2, int(n * valid_frac))
    test = shuffled[:n_test]
    valid = shuffled[n_test : n_test + n_valid]
    train = shuffled[n_test + n_valid :]
    if not train:
        raise ValueError("train split is empty — add more examples")

    dest.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, rows in (("train", train), ("valid", valid), ("test", test)):
        path = dest / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for user, assistant in rows:
                fh.write(json.dumps(chat_row(system, user, assistant), ensure_ascii=False))
                fh.write("\n")
        counts[name] = len(rows)
    return counts
