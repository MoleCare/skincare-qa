# Security Policy

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

Email **info@molecare.co.uk** with:

- what the issue is and where in the code it lives
- how to reproduce it
- what an attacker could do with it

You should get an acknowledgement within **3 working days**. We will tell you
when we have a fix and will credit you in the release notes unless you would
rather we did not.

On GitHub, the Security tab "Report a vulnerability" button is also fine if
the repository has it enabled.

## Scope

In scope:

- the HTTP sidecar (`scripts/serve.py`) — prompt injection into logs, SSRF if
  `OLLAMA_HOST` is attacker-controlled, unbounded body size
- harness misses that ship a **blocked** class of output (`pass` on a diagnosis
  string, a leaked key, or `curl|sh`)
- secrets committed to the repository
- dependency issues that are reachable from `scripts/serve.py` or the harness

Out of scope for a vulnerability report (open a normal issue / PR instead):

- paraphrase evasion of string rules — same limit as skin-care-harness
- model quality / wrong educational facts
- needing a Hugging Face token to train

## Data safety

- Never attach a real skin photo to an issue or pull request
- Never commit `.env`, `HF_TOKEN`, or adapter folders that were trained on
  private images
- Training JSONL in this repo is educational text from public MoleCare
  sources, not patient records

If you believe patient data has been committed, use the private channel above
and do not open an issue that points at the file.
