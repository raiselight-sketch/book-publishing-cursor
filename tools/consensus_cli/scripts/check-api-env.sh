#!/usr/bin/env bash
# API 키 값은 출력하지 않고, 길이·접두사만 확인 (401 진단용)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=""
.venv/bin/python <<'PY'
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(".env"))

def peek(name):
    v = os.environ.get(name) or ""
    v = v.strip().strip('"').strip("'")
    if not v:
        return "없음"
    n = len(v)
    bad = "\n" in v or "\r" in v
    pre = v[:7] if n >= 7 else v[:n]
    extra = " (값 안에 줄바꿈 의심)" if bad else ""
    return f"길이={n}, 시작={pre!r}…{extra}"

for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
    print(f"{k}: {peek(k)}")
PY
