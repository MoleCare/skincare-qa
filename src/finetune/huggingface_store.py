"""Save fused weights and adapters on https://huggingface.co/YauhenBichel."""

from __future__ import annotations

import os
from pathlib import Path

from finetune.models import HF_USER, ModelSpec
from finetune.paths import PROJECT_ROOT

CARDS = PROJECT_ROOT / "cards"


def require_token() -> str:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token
    try:
        from huggingface_hub import get_token

        token = get_token()
    except Exception:
        token = None
    if not token:
        raise SystemExit(
            "No Hugging Face token. Run `huggingface-cli login` or export HF_TOKEN. "
            f"Uploads go to https://huggingface.co/{HF_USER}"
        )
    return token


def write_card(spec: ModelSpec, dest: Path) -> Path:
    src = CARDS / f"{spec.name}.md"
    if not src.is_file():
        raise FileNotFoundError(src)
    dest.mkdir(parents=True, exist_ok=True)
    readme = dest / "README.md"
    readme.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return readme


def push_folder(spec: ModelSpec, folder: Path, *, private: bool, token: str) -> str:
    if not folder.is_dir() or not any(folder.iterdir()):
        raise FileNotFoundError(f"nothing to upload in {folder}")
    from huggingface_hub import HfApi

    write_card(spec, folder)
    api = HfApi(token=token)
    api.create_repo(spec.hf_repo, repo_type="model", private=private, exist_ok=True)
    api.upload_folder(
        folder_path=str(folder),
        repo_id=spec.hf_repo,
        repo_type="model",
        commit_message=f"save {spec.name} ({folder.name})",
    )
    return f"https://huggingface.co/{spec.hf_repo}"


def pull_folder(spec: ModelSpec, dest: Path, *, token: str | None) -> Path:
    from huggingface_hub import snapshot_download

    dest.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=spec.hf_repo,
        local_dir=str(dest),
        token=token,
    )
    return dest
