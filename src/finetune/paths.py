"""Default locations for MoleCare checkouts and this project's outputs."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
ADAPTERS_ROOT = PROJECT_ROOT / "adapters"
FUSED_ROOT = PROJECT_ROOT / "fused"
CONFIGS_ROOT = PROJECT_ROOT / "configs"

MOLECARE_ROOT = Path.home() / "DevBox" / "molecare"
MCP_KB = MOLECARE_ROOT / "molecare-mcp" / "src" / "resources" / "medical-kb.ts"
WEBAPP_I18N = MOLECARE_ROOT / "molecare-webapp" / "public" / "locales" / "en" / "translation.json"
HARNESS_PYTHON = MOLECARE_ROOT / "skin-care-harness" / "packages" / "python"
CLAUDE_CHAT = (
    MOLECARE_ROOT
    / "molecare-server"
    / "src"
    / "main"
    / "java"
    / "com"
    / "twoay"
    / "molecare"
    / "chat"
    / "service"
    / "ClaudeChatService.java"
)
