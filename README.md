# 책출판 (book project)

이 저장소는 **한국어 도서** 원고·기획·퇴고를 Cursor에서 진행하기 위한 작업 공간이다.

## Cursor 스킬: `book-writing`

프로젝트 전용 스킬 경로:

`.cursor/skills/book-writing/SKILL.md`

책 기획부터 투고·마케팅까지의 워크플로가 정리되어 있으며, 세부 템플릿은 `references/`를 참고한다.

### 다른 프로젝트에서 쓰려면

이 폴더 전체를 복제하거나, `book-writing` 디렉터리만 원하는 프로젝트의 `.cursor/skills/` 아래에 복사하면 된다.

## 원고 폴더 구조 (권장)

| 경로 | 용도 |
|------|------|
| `manuscript/outline.md` | 한 줄 코어 문장, 목차, 챕터 메모 |
| `manuscript/chapters/` | 챕터별 마크다운 (`01-제목.md` 형식 권장) |
| `manuscript/front-matter.md` | 프롤로그, 추천의 글 초안 |
| `manuscript/research/notebook-lm/` | [NotebookLM](manuscript/research/notebook-lm/README.md)에서 보낸 자료·요약·인용 스니펫 (미러링) |
| `manuscript/research/prompts/` | Gems·커스텀 시스템 지시 등 (예: 집단 놀이 치료 가이드 프롬프트) |
| `manuscript/assets/` | [사진·AI 삽화·도판](manuscript/assets/README.md) (`photos/`, `ai-generated/`, `figures/`) |

한글(HWP)·워드(DOCX)로 제출할 때는 여기서 다듬은 뒤 옮겨 적거나내면 된다.

## 다중 LLM 합의 CLI

Gemini·ChatGPT·Claude·Ollama(Gemma 등)가 초안 → 상호 통합 → 투표로 최종안을 고른다.

설치·사용: [tools/consensus_cli/README.md](tools/consensus_cli/README.md)

## GitHub

원격 저장소: [https://github.com/raiselight-sketch/book-publishing-cursor](https://github.com/raiselight-sketch/book-publishing-cursor)

다른 계정·저장소 이름으로 옮길 때는 `git remote set-url origin …` 후 `git push` 하면 된다.
