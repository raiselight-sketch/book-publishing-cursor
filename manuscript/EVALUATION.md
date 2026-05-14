# 다중 AI 평가·합의 (터미널)

책 원고 일부를 **여러 모델이 초안 → 통합 → 투표**로 거친 뒤, **한 가지 최종안**을 고르게 하려면 `book-consensus` CLI를 쓴다.

## 1) API 키 넣기 (한 번만)

터미널에서 **이 폴더로 이동**한 뒤 `.env`를 만든다.

```bash
cd "/Users/raiselight/ai 자동화/책출판/tools/consensus_cli"
cp .env.example .env
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

## 4) 결과 반영

- 터미널에 나온 **최종 합의** 문단을 `manuscript/chapters/` 또는 `exports` 퇴고본에 반영한다.
- `--json-out`으로 저장한 파일에는 라운드별 요약이 있어, 어떤 모델이 무엇을 말했는지 추적할 수 있다.

자세한 옵션: [tools/consensus_cli/README.md](../tools/consensus_cli/README.md)
