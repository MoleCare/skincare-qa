#!/usr/bin/env python3
"""Tiny HTTP sidecar: Ollama generates, the matching harness decides.

  PYTHONPATH=src python scripts/serve.py
  curl -s localhost:8080/health
  curl -s localhost:8080/v1/skincare-qa -d '{"prompt":"what is ABCDE?"}' -H 'content-type: application/json'
  curl -s localhost:8080/v1/python-vibe -d '{"prompt":"jsonl reader"}' -H 'content-type: application/json'
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finetune.models import SPECS  # noqa: E402
from harness.fallbacks import PYTHON_VIBE_FALLBACK, SKINCARE_FALLBACK  # noqa: E402
from harness.ollama_generate import OllamaGenerate  # noqa: E402
from harness.python_vibe import PythonVibeGuard  # noqa: E402
from harness.run import complete  # noqa: E402
from harness.skincare import SkincareGuard  # noqa: E402


def _routes():
    py = SPECS["python-vibe"]
    skin = SPECS["skincare-qa"]
    return {
        "/v1/python-vibe": (
            OllamaGenerate(py.ollama_base, py.system),
            PythonVibeGuard(),
            PYTHON_VIBE_FALLBACK,
        ),
        "/v1/skincare-qa": (
            OllamaGenerate(skin.ollama_base, skin.system),
            SkincareGuard(),
            SKINCARE_FALLBACK,
        ),
    }


ROUTES = _routes()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/health":
            self._json(404, {"error": "not found"})
            return
        backends = {
            name: generate.healthy()
            for name, (generate, _, _) in (
                ("python-vibe", ROUTES["/v1/python-vibe"]),
                ("skincare-qa", ROUTES["/v1/skincare-qa"]),
            )
        }
        self._json(200, {"ok": True, "ollama": backends, "models": {
            name: {
                "ollama": spec.ollama_base,
                "hf": f"https://huggingface.co/{spec.hf_repo}",
                "ram_mb": spec.ram_mb,
            }
            for name, spec in SPECS.items()
        }})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        route = ROUTES.get(path)
        if route is None:
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or "0")
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        prompt = (body.get("prompt") or "").strip()
        if not prompt:
            self._json(400, {"error": "prompt required"})
            return
        red_flags = list(body.get("red_flags") or [])
        generate, guard, fallback = route
        try:
            outcome = complete(generate, guard, fallback, prompt, red_flags=red_flags)
        except RuntimeError as exc:
            self._json(502, {"error": str(exc)})
            return
        self._json(
            200,
            {
                "text": outcome.output,
                "verdict": outcome.verdict,
                "fallback": outcome.fallback,
                "findings": [
                    {"rule_id": f.rule_id, "severity": f.severity, "excerpt": f.excerpt}
                    for f in outcome.findings
                ],
                "ruleset": outcome.ruleset_version,
            },
        )


def main() -> None:
    host = "0.0.0.0"
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"harness listening on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
