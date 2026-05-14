#!/usr/bin/env bash
# 책 원고 조각(마크다운)을 book-consensus로 돌린다. 저장소 루트 기준 상대 경로를 넘길 수 있다.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

if [[ $# -lt 1 ]] || [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
  echo "사용법: $0 <평가할.md 경로> [book-consensus 추가 옵션…]"
  echo "예: $0 manuscript/snippets/eval-001.md"
  echo "예: $0 manuscript/snippets/eval-001.md --json-out manuscript/snippets/out.json -p openai,anthropic"
  exit 0
fi

INPUT="$1"
shift

if [[ -f "$INPUT" ]]; then
  PROMPT_FILE="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
elif [[ -f "$REPO_ROOT/$INPUT" ]]; then
  PROMPT_FILE="$REPO_ROOT/$INPUT"
else
  echo "파일을 찾을 수 없습니다: $INPUT (현재 디렉터리 또는 저장소 루트 기준)"
  exit 1
fi

cd "$CLI_ROOT"

if [[ ! -f .env ]]; then
  echo "[오류] $CLI_ROOT/.env 가 없습니다."
  echo "  cp .env.example .env  후 API 키를 채우세요."
  echo "  안내: manuscript/EVALUATION.md"
  exit 1
fi

if [[ -f .venv/bin/book-consensus ]]; then
  BC=(.venv/bin/book-consensus)
elif command -v book-consensus >/dev/null 2>&1; then
  BC=(book-consensus)
else
  echo "[오류] book-consensus 가 없습니다."
  echo "  cd \"$CLI_ROOT\" && python3 -m venv .venv && .venv/bin/pip install -e ."
  exit 1
fi

exec "${BC[@]}" --prompt-file "$PROMPT_FILE" "$@"
