# Contributing

This tree trains two small LoRA models and wraps each in a deterministic
harness. It is **Apache-2.0**, easy to run locally, and meant for first-time
contributors — if you keep the safety rules below.

## The rule that is not negotiable (skincare-qa)

**This project must never produce, imply, or imitate a medical diagnosis.**

`skincare-qa` is educational skin-health Q&A. It is not a medical device.
Any change that moves an answer closer to "this lesion is / isn't melanoma"
will be declined, however good the code or the loss curve is.

Same table as [molecare-mcp](https://github.com/MoleCare/molecare-mcp):

| Fine | Not fine |
|---|---|
| "The ABCDE criteria describe asymmetry, border, colour, diameter, evolution." | "This mole scores 4/5 on ABCDE, likely melanoma." |
| "Irregular borders are one feature clinicians assess." | "Irregular border detected — seek urgent care." |
| A confidence on a **photo-quality** check ("too dark, retake") | A confidence used as a verdict on the person's mole |

New skincare training rows must pass MoleCare `skin-care-harness`
(`PYTHONPATH=src python scripts/build_data.py` fails on a `block`).

`python-vibe` is not a health model. Do not teach it to comment on lesions
(the python harness already blocks that).

## Getting set up (no cloud, no secrets)

```bash
git clone https://github.com/MoleCare/skincare-qa.git   # or this workbench path
cd llm-finetunes   # if cloned from the workbench
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # MLX train — macOS Apple Silicon
# harness tests only (Linux CI / no GPU):
python -m unittest discover -s tests -q
```

You do **not** need a Hugging Face token, Ollama, AWS, or a MoleCare API key
to run the harness tests. Training downloads public 4-bit bases from
`mlx-community/*`.

`skin-care-harness` tests skip if that checkout is missing. Clone it next to
this repo at `~/DevBox/molecare/skin-care-harness` (or set the path in
`src/finetune/paths.py`).

## What you may add

- More **educational** Q&A pairs sourced from [molecare-mcp](https://github.com/MoleCare/molecare-mcp) knowledge, not from lesion photos
- Harness rules with **fixtures** (a fail string and a near-miss pass)
- Docs, CI, and eval prompts that never include a real skin photo

## What you must not add

- Patient photos, even as "fake" fixtures that are real pictures
- Hugging Face / cloud tokens, private keys, or production hostnames
- A keyword router on the **user** prompt that skips the harness
- Diagnostic labels from [google/derm-foundation](https://huggingface.co/google/derm-foundation) or molecare-ml into training text
- `curl … \| sh` examples that the python harness would block

## Before you open a pull request

- [ ] `python -m unittest discover -s tests -q` passes
- [ ] `PYTHONPATH=src python scripts/build_data.py` passes if you touched skincare pairs
- [ ] New medical answers include the educational disclaimer
- [ ] No secrets, real hostnames, or personal data
- [ ] No patient images

## Pull requests

One concern per PR. Say what a user can do now that they could not before.
Large refactors: open an issue first.

## Reporting security issues

Do **not** open a public issue. See [SECURITY.md](./SECURITY.md).

## Licence

By contributing you agree that your contributions are licensed under the
[Apache-2.0 licence](./LICENSE) that covers this project.
