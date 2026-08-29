#!/usr/bin/env python3
"""Upload fused weights (or adapters) to https://huggingface.co/YauhenBichel."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finetune.huggingface_store import push_folder, require_token  # noqa: E402
from finetune.models import SPECS  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", choices=sorted(SPECS))
    parser.add_argument(
        "--what",
        choices=("fused", "adapters"),
        default="fused",
        help="fused model folder is the big artifact; adapters are the small LoRA files",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="create/update a public repo (default is private)",
    )
    args = parser.parse_args()
    spec = SPECS[args.model]
    folder = spec.fused_path if args.what == "fused" else spec.adapter_path
    url = push_folder(spec, folder, private=not args.public, token=require_token())
    print(url)


if __name__ == "__main__":
    main()
