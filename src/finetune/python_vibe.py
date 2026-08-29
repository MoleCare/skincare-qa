"""Python vibe-coding pairs — working code first, short note after."""

from __future__ import annotations


def all_pairs() -> list[tuple[str, str]]:
    return list(_PAIRS)


_PAIRS: list[tuple[str, str]] = [
    (
        "Write a script that lists the largest files under a directory.",
        """Walks with `pathlib`, sorts by size, prints a table.

```python
#!/usr/bin/env python3
from pathlib import Path
import argparse

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path, default=Path("."), nargs="?")
    p.add_argument("-n", type=int, default=20)
    args = p.parse_args()
    files = [f for f in args.root.rglob("*") if f.is_file()]
    files.sort(key=lambda f: f.stat().st_size, reverse=True)
    for f in files[: args.n]:
        print(f"{f.stat().st_size:>12}  {f}")

if __name__ == "__main__":
    main()
```
""",
    ),
    (
        "JSONL reader that yields dicts and skips bad lines.",
        """Don't crash the whole file on one bad row.

```python
import json
from collections.abc import Iterator
from pathlib import Path

def read_jsonl(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"skip {path}:{line_no}: {exc}")
                continue
            if isinstance(row, dict):
                yield row
```
""",
    ),
    (
        "Tiny FastAPI ping + echo.",
        """One file. Run with `uvicorn app:app --reload`.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Echo(BaseModel):
    text: str

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/echo")
def echo(body: Echo) -> Echo:
    return body
```
""",
    ),
    (
        "Retry a function three times with backoff.",
        """Stdlib only.

```python
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def retry(fn: Callable[[], T], *, attempts: int = 3, base: float = 0.2) -> T:
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            time.sleep(base * (2 ** i))
    assert last is not None
    raise last
```
""",
    ),
    (
        "Async gather with a timeout per task.",
        """`asyncio.wait_for` per call, then `gather`.

```python
import asyncio
from collections.abc import Awaitable, Sequence
from typing import TypeVar

T = TypeVar("T")

async def gather_timeout(
    aws: Sequence[Awaitable[T]], timeout: float
) -> list[T | BaseException]:
    wrapped = [asyncio.wait_for(aw, timeout) for aw in aws]
    return list(await asyncio.gather(*wrapped, return_exceptions=True))
```
""",
    ),
    (
        "pytest: temp file in, expected string out.",
        """Fixture writes the input; assert the function.

```python
from pathlib import Path
import pytest
from mypkg.io import slugify_file

def test_slugify_file(tmp_path: Path) -> None:
    src = tmp_path / "Hello World.TXT"
    src.write_text("x", encoding="utf-8")
    out = slugify_file(src)
    assert out.name == "hello-world.txt"
```
""",
    ),
    (
        "Parse a .env file into a dict. No extra libs.",
        """Ignore comments and blank lines. Last key wins.

```python
from pathlib import Path

def load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip("\"'")
    return out
```
""",
    ),
    (
        "Dedup a list of dicts by (name, version) without json.dumps.",
        """Tuple keys, not stringified JSON.

```python
def unique_packages(rows: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for row in rows:
        key = (row["name"], row["version"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out
```
""",
    ),
    (
        "Context manager that cd's and comes back.",
        """

```python
from contextlib import contextmanager
from pathlib import Path
import os
from collections.abc import Iterator

@contextmanager
def pushd(path: Path) -> Iterator[None]:
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)
```
""",
    ),
    (
        "SQLite insert-or-ignore for a url cache.",
        """

```python
import sqlite3
from pathlib import Path

def open_cache(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS pages (url TEXT PRIMARY KEY, body TEXT)"
    )
    return conn

def put(conn: sqlite3.Connection, url: str, body: str) -> None:
    conn.execute("INSERT OR IGNORE INTO pages(url, body) VALUES (?, ?)", (url, body))
    conn.commit()
```
""",
    ),
    (
        "httpx GET with a hard timeout and raise for status.",
        """

```python
import httpx

def fetch_text(url: str, timeout: float = 10.0) -> str:
    with httpx.Client(timeout=timeout) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
```
""",
    ),
    (
        "dataclass for a train example, frozen.",
        """

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Example:
    user: str
    assistant: str

    def as_pair(self) -> tuple[str, str]:
        return self.user, self.assistant
```
""",
    ),
    (
        "argparse: required input file, optional --out, default stdout.",
        """

```python
import argparse
import sys
from pathlib import Path

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Transform a file")
    p.add_argument("src", type=Path)
    p.add_argument("--out", type=Path)
    return p

def main() -> None:
    args = build_parser().parse_args()
    text = args.src.read_text(encoding="utf-8")
    if args.out:
        args.out.write_text(text.upper(), encoding="utf-8")
    else:
        sys.stdout.write(text.upper())
```
""",
    ),
    (
        "Split a list into chunks of n.",
        """

```python
from collections.abc import Iterator, Sequence
from typing import TypeVar

T = TypeVar("T")

def chunks(items: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    if n <= 0:
        raise ValueError("n must be > 0")
    for i in range(0, len(items), n):
        yield items[i : i + n]
```
""",
    ),
    (
        "logging setup that isn't ugly.",
        """One call at the entrypoint.

```python
import logging

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
```
""",
    ),
    (
        "Filter None from a list and keep types honest.",
        """

```python
from typing import TypeVar

T = TypeVar("T")

def present(items: list[T | None]) -> list[T]:
    return [item for item in items if item is not None]
```
""",
    ),
    (
        "Read stdin, count words, print top 10.",
        """

```python
import sys
from collections import Counter
import re

words = re.findall(r"[A-Za-z']+", sys.stdin.read().lower())
for word, n in Counter(words).most_common(10):
    print(f"{n:>6}  {word}")
```
""",
    ),
    (
        "Make a pathlib helper that refuses to write outside a root.",
        """Stops `../` surprises.

```python
from pathlib import Path

def safe_join(root: Path, relative: str) -> Path:
    dest = (root / relative).resolve()
    if not dest.is_relative_to(root.resolve()):
        raise ValueError(f"escape: {relative}")
    return dest
```
""",
    ),
    (
        "Pydantic v2 model for a chat message.",
        """

```python
from typing import Literal
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)
```
""",
    ),
    (
        "Replace a nested key in a dict without deepcopy.",
        """Mutate a shallow copy of the path.

```python
def set_path(row: dict, path: tuple[str, ...], value: object) -> dict:
    if not path:
        raise ValueError("empty path")
    out = dict(row)
    cur = out
    for key in path[:-1]:
        nxt = dict(cur.get(key) or {})
        cur[key] = nxt
        cur = nxt
    cur[path[-1]] = value
    return out
```
""",
    ),
    (
        "Watch a directory and print new files. No watchdog lib.",
        """Poll mtime. Good enough for a local tool.

```python
import time
from pathlib import Path

def watch(root: Path, seconds: float = 1.0) -> None:
    seen = {p: p.stat().st_mtime for p in root.glob("*") if p.is_file()}
    while True:
        time.sleep(seconds)
        for path in root.glob("*"):
            if not path.is_file():
                continue
            mtime = path.stat().st_mtime
            if path not in seen or seen[path] < mtime:
                print(path)
                seen[path] = mtime
```
""",
    ),
    (
        "Turn a traceback into a one-liner for logs. Don't leak to users.",
        """Log server-side; return a boring string to the client.

```python
import logging
import traceback

log = logging.getLogger("app")

def handle(exc: Exception) -> str:
    log.exception("request failed")
    return "internal error"
```
""",
    ),
    (
        "Minimal Makefile-less test runner: python -m pytest tests -q",
        """Put this in a justfile or alias. That's the vibe.

```text
python -m pytest tests -q --tb=short
```
""",
    ),
    (
        "Generator that yields matching lines from a huge log.",
        """Don't read the whole file.

```python
from collections.abc import Iterator
from pathlib import Path

def grep(path: Path, needle: str) -> Iterator[str]:
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if needle in line:
                yield line.rstrip("\\n")
```
""",
    ),
    (
        "dataclass + Path for CLI config loaded from JSON.",
        """

```python
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    root: Path
    workers: int = 4

    @classmethod
    def load(cls, path: Path) -> "Config":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(root=Path(raw["root"]), workers=int(raw.get("workers", 4)))
```
""",
    ),
    (
        "Fix this: except: pass",
        """Catch what you mean. Log it.

```python
import logging

log = logging.getLogger(__name__)

try:
    payload = load()
except (OSError, ValueError) as exc:
    log.warning("load failed: %s", exc)
    payload = {}
```
""",
    ),
    (
        "Thread pool for a list of CPU-light tasks.",
        """I/O bound → threads. CPU bound → processes.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

def map_threads(fn: Callable[[T], R], items: Iterable[T], workers: int = 8) -> list[R]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(fn, item) for item in items]
        return [fut.result() for fut in as_completed(futs)]
```
""",
    ),
    (
        "Pretty-print a table without pandas.",
        """

```python
def print_table(rows: list[tuple[str, ...]]) -> None:
    if not rows:
        return
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
```
""",
    ),
    (
        "Enum for job status, plus a terminal check.",
        """

```python
from enum import StrEnum

class Status(StrEnum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"

    def terminal(self) -> bool:
        return self in {Status.done, Status.failed}
```
""",
    ),
    (
        "sha256 of a file in 1MB chunks.",
        """

```python
import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
```
""",
    ),
    (
        "Typed CLI using only argparse subcommands: add and ls.",
        """

```python
import argparse

def add(args: argparse.Namespace) -> None:
    print(args.a + args.b)

def ls(_: argparse.Namespace) -> None:
    print("ok")

def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(required=True)
    add_p = sub.add_parser("add")
    add_p.add_argument("a", type=int)
    add_p.add_argument("b", type=int)
    add_p.set_defaults(fn=add)
    ls_p = sub.add_parser("ls")
    ls_p.set_defaults(fn=ls)
    args = p.parse_args()
    args.fn(args)
```
""",
    ),
    (
        "Freeze requirements from the current venv the boring way.",
        """

```bash
python -m pip freeze > requirements.lock
```
""",
    ),
    (
        "Match glob **/*.py and skip .venv.",
        """

```python
from pathlib import Path

def py_files(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*.py")
        if ".venv" not in p.parts and "__pycache__" not in p.parts
    ]
```
""",
    ),
    (
        "httpx + tenacity? nah, just a loop.",
        """Keep it boring.

```python
import time
import httpx

def get_ok(url: str) -> httpx.Response:
    last: Exception | None = None
    for i in range(4):
        try:
            r = httpx.get(url, timeout=10)
            r.raise_for_status()
            return r
        except httpx.HTTPError as exc:
            last = exc
            time.sleep(0.25 * (i + 1))
    raise last  # type: ignore[misc]
```
""",
    ),
    (
        "Split train/valid ids with a seed. No sklearn.",
        """

```python
import random

def split_ids(ids: list[str], valid_frac: float = 0.1, seed: int = 0) -> tuple[list[str], list[str]]:
    rng = random.Random(seed)
    shuffled = list(ids)
    rng.shuffle(shuffled)
    n_valid = max(1, int(len(shuffled) * valid_frac))
    return shuffled[n_valid:], shuffled[:n_valid]
```
""",
    ),
    (
        "Write JSON atomically (temp file + replace).",
        """

```python
import json
import os
from pathlib import Path

def write_json(path: Path, data: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\\n", encoding="utf-8")
    os.replace(tmp, path)
```
""",
    ),
    (
        "dataclass slots for a hot row.",
        """

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Row:
    name: str
    n: int
```
""",
    ),
    (
        "How do I run a module as a script in a src layout?",
        """From the repo root, with `src` on the path:

```bash
PYTHONPATH=src python -m finetune.whatever
```

Or install the package editable and drop PYTHONPATH.
""",
    ),
    (
        "Type a JSONL stream as list[dict[str, object]].",
        """Don't pretend you know the schema if you don't.

```python
import json
from pathlib import Path

def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
```
""",
    ),
    (
        "Kill a hung subprocess after N seconds.",
        """

```python
import subprocess

def run_capped(cmd: list[str], seconds: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=True,
        timeout=seconds,
    )
```
""",
    ),
    (
        "Sort paths so 2 comes before 10.",
        """Natural sort on the name.

```python
import re
from pathlib import Path

_NUM = re.compile(r"(\\d+)")

def key(path: Path) -> tuple:
    parts = _NUM.split(path.name)
    return tuple(int(p) if p.isdigit() else p.lower() for p in parts)
```
""",
    ),
    (
        "One-liner to start a venv and install mlx on 3.13.",
        """

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install 'mlx-lm[train]'
```
""",
    ),
    (
        "Don't use mutable default args.",
        """

```python
def add_tag(row: dict, tag: str, tags: list[str] | None = None) -> list[str]:
    out = list(tags or [])
    out.append(tag)
    row["tags"] = out
    return out
```
""",
    ),
    (
        "Zip two lists and drop extras — or keep them?",
        """`zip` drops. `itertools.zip_longest` keeps.

```python
from itertools import zip_longest

def pairs(left: list[str], right: list[str]) -> list[tuple[str | None, str | None]]:
    return list(zip_longest(left, right))
```
""",
    ),
    (
        "Path.read_text vs open. Which?",
        """`Path.read_text(encoding='utf-8')` for whole files. `open` when you stream.

```python
from pathlib import Path

text = Path("notes.md").read_text(encoding="utf-8")
```
""",
    ),
]
