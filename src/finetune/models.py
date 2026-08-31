"""Small bases so both models fit a 1 GB cloud box (Ollama / llama.cpp).

MLX 4-bit IDs are for training on this Mac. Ollama tags are what you serve.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from finetune.paths import ADAPTERS_ROOT, FUSED_ROOT
from finetune.systems import SKINCARE_SYSTEM


HF_USER = "YauhenBichel"


@dataclass(frozen=True)
class ModelSpec:
    name: str
    mlx_base: str
    ollama_base: str
    hf_repo: str
    system: str
    adapter_path: Path
    fused_path: Path
    ram_mb: int


SPECS: dict[str, ModelSpec] = {
    "skincare-qa": ModelSpec(
        name="skincare-qa",
        mlx_base="mlx-community/Llama-3.2-1B-Instruct-4bit",
        ollama_base="llama3.2:1b",
        hf_repo=f"{HF_USER}/skincare-qa-1b",
        system=SKINCARE_SYSTEM,
        adapter_path=ADAPTERS_ROOT / "skincare-qa",
        fused_path=FUSED_ROOT / "skincare-qa",
        ram_mb=700,
    ),
}
