# Multi-LLM 합의 CLI (`book-consensus`)

Gemini, ChatGPT(OpenAI), Claude(Anthropic), Ollama(예: Gemma) 네 갈래가

1. **Round 1** — 같은 프롬프트에 대해 각자 초안 작성  
2. **Round 2** — 서로의 초안을 익명 라벨(A,B,…)로 보고 점수·평가·**통합 최종안**(`integrated_final`) 생성  
3. **Round 3** — 각 모델이 통합안들(T0,T1,…)에 투표 → **다수결**로 하나 선택  
4. 동표·파싱 실패 시 **`CONSENSUS_ARBITER_MODEL`**(기본: Claude 계열)이 최종 선택

## 설치

```bash
cd tools/consensus_cli
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

## 환경 변수

`cp .env.example .env` 후 값 채우기.

| 변수 | 설명 |
|------|------|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic |
| `GEMINI_API_KEY` | Google Gemini (litellm) |
| `OLLAMA_API_BASE` | 기본 `http://127.0.0.1:11434` |
| `CONSENSUS_MODEL_*` | 모델 ID 재정의 (`.env.example` 참고) |

Gemma 로컬 예: `ollama pull gemma3:4b` 후 `CONSENSUS_MODEL_OLLAMA=ollama/gemma3:4b`  
(태그는 설치한 모델명에 맞출 것.)

## 사용 예

```bash
book-consensus "이 책의 1장 훅 문단 3개를 제안해 줘"
book-consensus -f ../../manuscript/outline.md --json-out out.json
book-consensus "..." -p gemini,anthropic --quiet > final.txt
book-consensus "..." --skip-vote   # 3차 투표 없이 중재자만
```

표준 입력:

```bash
cat prompt.txt | book-consensus
```

## 주의

- API 비용이 **모델 수 × 라운드**만큼 듭니다. 테스트는 `-p openai,ollama` 처럼 줄이세요.  
- Ollama는 로컬 데몬이 떠 있어야 합니다.
