#!/usr/bin/env python3
"""Download a saved model from https://huggingface.co/YauhenBichel into fused/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finetune.huggingface_store import pull_folder, require_token  # noqa: E402
from finetune.models import SPECS  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", choices=sorted(SPECS))
    args = parser.parse_args()
    spec = SPECS[args.model]
    dest = pull_folder(spec, spec.fused_path, token=require_token())
    print(dest)


if __name__ == "__main__":
    main()
