"""Default locations for MoleCare checkouts and this project's outputs."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
ADAPTERS_ROOT = PROJECT_ROOT / "adapters"
FUSED_ROOT = PROJECT_ROOT / "fused"
CONFIGS_ROOT = PROJECT_ROOT / "configs"


def _environment_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


MOLECARE_ROOT = _environment_path("MOLECARE_ROOT", PROJECT_ROOT.parent)
MCP_KB = MOLECARE_ROOT / "molecare-mcp" / "src" / "resources" / "medical-kb.ts"
WEBAPP_I18N = MOLECARE_ROOT / "molecare-webapp" / "public" / "locales" / "en" / "translation.json"
HARNESS_PYTHON = _environment_path(
    "SKIN_CARE_HARNESS_PYTHON",
    MOLECARE_ROOT / "skin-care-harness" / "packages" / "python",
)
