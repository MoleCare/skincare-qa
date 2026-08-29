# Two small LoRA models + harnesses

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)
[![CI](https://github.com/MoleCare/skincare-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/MoleCare/skincare-qa/actions/workflows/ci.yml)

**Not a medical device.** Public repos:
[MoleCare/skincare-qa](https://github.com/MoleCare/skincare-qa) ·
[YauhenBichel/python-vibe](https://github.com/YauhenBichel/python-vibe).

Contributing: [CONTRIBUTING.md](./CONTRIBUTING.md) · security: [SECURITY.md](./SECURITY.md).
Vulnerabilities go to **info@molecare.co.uk**, not a public issue.

Sized for a cheap cloud box (about **1 GB RAM** together), not a GPU pod.

| Name | Job | Base (4-bit) | Size | Cloud tag | Harness |
|---|---|---|---|---|---|
| `python-vibe` | Python vibe coding | Qwen2.5-Coder-**0.5B** | ~400 MB | `qwen2.5-coder:0.5b` | `PythonVibeGuard` |
| `skincare-qa` | Skin-health Q&A | Llama-3.2-**1B** | ~700 MB | `llama3.2:1b` | MoleCare `skin-care-harness` |

MLX is only for **training on this Mac**. Serving is Ollama + a tiny Python sidecar. The sidecar has no weights.

```
client → harness :8080 → ollama (0.5B / 1B)
              ↓
     pass / revise / block
     block twice → fixed fallback
```

Same pattern as [skin-care-harness example 02](https://github.com/MoleCare/skin-care-harness): the model drafts, the harness decides whether that draft ships. The harness is not a second model.

## Harnesses

| Surface | What it checks | On block |
|---|---|---|
| `/v1/skincare-qa` | MoleCare `SkinGuard` (no diagnosis, no "that's benign") | regenerate once, then the MoleCare safe fallback |
| `/v1/python-vibe` | empty, leaked keys, `curl\|sh`, lesion diagnosis (wrong surface) | regenerate once, then a short refusal |

Skincare rules are **not** copied. They load from a sibling
`skin-care-harness` checkout (`packages/python`), or from
`SKIN_CARE_HARNESS_PYTHON` / `MOLECARE_ROOT`.

## Train (Mac / MLX 3.13)

```bash
git clone https://github.com/MoleCare/skincare-qa.git
cd skincare-qa
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python scripts/build_data.py
PYTHONPATH=src python scripts/train.py python-vibe
PYTHONPATH=src python scripts/train.py skincare-qa
```

Data for `skincare-qa` still comes from [molecare-mcp](https://github.com/MoleCare/molecare-mcp) + [molecare-webapp](https://github.com/MoleCare/molecare-webapp). `molecare-ml` is image CNNs — unused.

## Serve (cloud or laptop)

Pull the tiny bases (you already have `llama3.2:1b`):

```bash
ollama pull qwen2.5-coder:0.5b
ollama pull llama3.2:1b
```

```bash
PYTHONPATH=src python scripts/serve.py          # :8080
PYTHONPATH=src python -m unittest discover -s tests -q
```

```bash
curl -s localhost:8080/health
curl -s localhost:8080/v1/skincare-qa \
  -H 'content-type: application/json' \
  -d '{"prompt":"What is the ABCDE rule?","red_flags":[]}'
curl -s localhost:8080/v1/python-vibe \
  -H 'content-type: application/json' \
  -d '{"prompt":"jsonl reader that skips bad lines"}'
```

Point the sidecar at a remote Ollama with `OLLAMA_HOST=http://ollama:11434`.

A 1 vCPU / 1–2 GB box is enough: Ollama holds the two 4-bit models, the harness is a few megabytes of Python.

## Chat through the harness

```bash
PYTHONPATH=src python scripts/chat.py skincare-qa "what is ABCDE?"
PYTHONPATH=src python scripts/chat.py python-vibe "write a jsonl reader"
```

## Save big artifacts on Hugging Face

Weights do not stay only on this Mac. After fuse, push to
[YauhenBichel](https://huggingface.co/YauhenBichel):

| Local name | Hugging Face repo |
|---|---|
| `python-vibe` | https://huggingface.co/YauhenBichel/python-vibe-0.5b |
| `skincare-qa` | https://huggingface.co/YauhenBichel/skincare-qa-1b |

```bash
hf auth login                  # or: huggingface-cli login / export HF_TOKEN=hf_...
PYTHONPATH=src python scripts/init_hf_repos.py   # cards only, creates the two repos
PYTHONPATH=src python scripts/fuse_and_export.py python-vibe --hf
PYTHONPATH=src python scripts/fuse_and_export.py skincare-qa --hf
# or after fuse:
PYTHONPATH=src python scripts/push_hf.py python-vibe --what fused
PYTHONPATH=src python scripts/pull_hf.py skincare-qa
```

Repos are **private** unless you pass `--public`. The model card is written
from `cards/`. Adapters (small) use `--what adapters`; fused MLX weights are
the large folder.
