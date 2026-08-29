"""--help on train, serve, and chat (issue #8). No model, no network."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _help(script: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout


class ScriptsHelpTest(unittest.TestCase):
    def test_serve_help_names_host_and_port(self) -> None:
        text = _help("serve.py")
        self.assertIn("8080", text)
        self.assertIn("0.0.0.0", text)

    def test_train_help(self) -> None:
        text = _help("train.py")
        self.assertIn("--iters", text)
        self.assertIn("--resume", text)

    def test_chat_help(self) -> None:
        text = _help("chat.py")
        self.assertIn("prompt", text)
        self.assertIn("--red-flag", text)


if __name__ == "__main__":
    unittest.main()
