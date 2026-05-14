# 다중 AI 평가·합의 (터미널)

책 원고 일부를 **여러 모델이 초안 → 통합 → 투표**로 거친 뒤, **한 가지 최종안**을 고르게 하려면 `book-consensus` CLI를 쓴다.

## 1) API 키 넣기 (한 번만)

터미널에서 **이 폴더로 이동**한 뒤 `.env`를 만든다.

```bash
cd "/Users/raiselight/ai 자동화/책출판/tools/consensus_cli"
cp .env.example .env
open -e .env
```

### 다시 처음부터 설정할 때

기존 `.env`는 **날짜 붙은 백업**으로 남기고 예시로 덮어씁니다.

```bash
cd "/Users/raiselight/ai 자동화/책출판/tools/consensus_cli"
chmod +x scripts/reset-api-env.sh   # 최초 1회
./scripts/reset-api-env.sh
open -e .env
```

`.env` 안에 **본인 키만** 채운다 (절대 Git에 커밋하지 말 것 — 이미 `.gitignore` 처리됨).

| 변수 | 용도 |
|------|------|
| `OPENAI_API_KEY` | ChatGPT(OpenAI) API |
| `ANTHROPIC_API_KEY` | Claude |
| `GEMINI_API_KEY` | Google Gemini (litellm) |
| `OLLAMA_API_BASE` | 로컬 Ollama (기본 `http://127.0.0.1:11434`) |

가상환경이 없으면:

```bash
cd "/Users/raiselight/ai 자동화/책출판/tools/consensus_cli"
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) 평가할 조각 만들기

장문 전체를 한 번에 넣으면 **비용·토큰**이 큼. `manuscript/snippets/`에 짧은 파일을 만든다.

예: `manuscript/snippets/eval-001.md`

```markdown
아래 원고 단락을 퇴고하라. 문장 호흡·중복 제거·교사 독자 톤 유지. 결과는 하나의 완성 문단으로.

---

(여기에 원고 붙여넣기)
```

## 3) 평가 실행

저장소 **어느 경로에서든** 다음 스크립트를 쓸 수 있다.

```bash
"/Users/raiselight/ai 자동화/책출판/tools/consensus_cli/scripts/evaluate-passage.sh" \
  "manuscript/snippets/eval-001.md"
```

JSON까지 남기려면:

```bash
"…/evaluate-passage.sh" "manuscript/snippets/eval-001.md" \
  --json-out "manuscript/snippets/eval-001-consensus.json"
```

모델을 줄이려면 (비용 절감):

```bash
"…/evaluate-passage.sh" "manuscript/snippets/eval-001.md" -p openai,anthropic
```

**한 개만** 쓰면 (`-p openai` 등) “다중 합의”가 아니라 **그 모델로 1회 응답**만 나옵니다. 연결 테스트·저비용 퇴고에 쓰면 됩니다. **진짜 합의(초안→통합→투표)** 는 `-p`에 **서로 다른 제공자를 2개 이상** 넣으세요.

## 4) 결과 반영

- 터미널에 나온 **최종 합의** 문단을 `manuscript/chapters/` 또는 `exports` 퇴고본에 반영한다.
- `--json-out`으로 저장한 파일에는 라운드별 요약이 있어, 어떤 모델이 무엇을 말했는지 추적할 수 있다.

자세한 옵션: [tools/consensus_cli/README.md](../tools/consensus_cli/README.md)

## 401 `Incorrect API key` (OpenAI)일 때

- 터미널 메시지의 `sk-....` 는 **OpenAI가 키를 가릴 때 쓰는 표시**일 수 있어, 반드시 `...` 세 글자를 넣었다는 뜻은 아닙니다.
- **플랫폼에서 새 시크릿 키**를 만들고 `.env`의 `OPENAI_API_KEY=` 뒤에 **한 줄로** 다시 붙여 넣습니다.
- 줄 끝·따옴표 문제를 줄이려면 CLI가 `.env`를 읽을 때 **앞뒤 공백·따옴표를 제거**하도록 이미 반영해 두었습니다. `pip install -e .` 경로에서 다시 실행해 보세요.
- 키 **길이·앞 7글자만** 보려면 (값 전체는 안 나옴):

```bash
cd "/Users/raiselight/ai 자동화/책출판/tools/consensus_cli"
./scripts/check-api-env.sh
```

- 터미널에 **`export OPENAI_API_KEY=`** 를 예전에 해 두었다면 빈 값이 우선될 수 있습니다. `unset OPENAI_API_KEY` 후 다시 시도해 보세요.
