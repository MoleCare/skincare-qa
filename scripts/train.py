#!/usr/bin/env python3
"""Run mlx_lm.lora for skincare-qa."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    "skincare-qa": ROOT / "configs" / "skincare-qa.yaml",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run mlx_lm.lora for skincare-qa. "
            "Defaults stay as they are; --iters and --resume are optional."
        )
    )
    parser.add_argument("model", choices=sorted(CONFIGS))
    parser.add_argument("--iters", type=int, default=None)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="continue from adapters/<model>/adapters.safetensors",
    )
    args = parser.parse_args()

    exe = shutil.which("mlx_lm.lora")
    if not exe:
        sys.exit("mlx_lm.lora not on PATH. Create the 3.13 venv and pip install -r requirements.txt")

    cmd = [exe, "--config", str(CONFIGS[args.model]), "--train"]
    if args.iters is not None:
        cmd.extend(["--iters", str(args.iters)])
    if args.resume:
        adapter = ROOT / "adapters" / args.model / "adapters.safetensors"
        if not adapter.is_file():
            sys.exit(f"no adapter to resume: {adapter}")
        cmd.extend(["--resume-adapter-file", str(adapter)])
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=ROOT)


if __name__ == "__main__":
    main()
