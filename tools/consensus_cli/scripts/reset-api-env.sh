#!/usr/bin/env bash
# 기존 .env 를 백업한 뒤 .env.example 으로 새 .env 를 만든다. (API 다시 설정할 때)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ -f .env ]]; then
  BAK=".env.backup.$(date +%Y%m%d-%H%M%S)"
  cp .env "$BAK"
  echo "기존 설정을 백업했습니다: $ROOT/$BAK"
fi
cp .env.example .env
echo "새 .env 를 만들었습니다: $ROOT/.env"
echo ""
echo "다음: 키를 채운 뒤 저장하세요."
echo "  open -e \"$ROOT/.env\""
echo "  또는 Cursor에서 tools/consensus_cli/.env 열기"
echo ""
echo "쓰지 않는 제공자 줄은 삭제하거나 비워 두어도 됩니다."
