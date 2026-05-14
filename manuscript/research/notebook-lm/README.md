# NotebookLM 자료 → 이 저장소 연결 가이드

NotebookLM(구글)에서 모은 자료는 **집필에 그대로 활용할 수 있다.**  
다만 **소비자용 NotebookLM은 “이 Git 폴더와 실시간 자동 동기화”하는 공식 API가 없다.** 그래서 아래처럼 **보내기·복사본을 이 폴더에 두는 방식**으로 “연결”하는 것이 가장 안정적이다.

## 활용 가능 여부

| 방식 | 가능 여부 | 설명 |
|------|-----------|------|
| 노트에 올린 PDF·문서·URL 요약 | ✅ | NotebookLM 안에서 요약·질의·아티팩트 생성에 활용됨. |
| Cursor/이 repo에서 그 자료를 읽기 | ✅ (간접) | **보낸 파일·복사한 마크다운**을 `manuscript/research/notebook-lm/`에 두면 Cursor가 인덱싱해 책 집필에 참고한다. |
| repo ↔ NotebookLM 실시간 양방향 동기화 | ❌ (일반 사용자) | 공식 소비자 API로는 제공되지 않는 경우가 대부분이다. |
| **NotebookLM Enterprise** (조직) | △ | Google Cloud 쪽 [노트북 API](https://cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks)로 관리·연동 범위가 달라질 수 있다. IT/계약 단위로 확인. |

## 권장 연결 절차 (미러링)

1. **NotebookLM에서** 노트북 이름을 “지금 집필 중인 책 제목”과 맞춘다.  
2. **자료보내기**  
   - 스튜디오에서 만든 **오디오 개요·마크다운·슬라이드** 등은 UI에서 저장 가능한 형식으로 받는다.  
   - 소스 원문이 필요하면 **원본 파일(PDF 등)을 Drive에 두고**, 그 사본을 이 폴더에 복사하거나, 허용되는 범위에서 **텍스트만 마크다운으로 정리**해 둔다.  
3. 이 저장소의 **`manuscript/research/notebook-lm/`** 아래에 저장한다.  
   - 예: `outline-from-nlm.md`, `sources-bibliography.md`, `quotes-and-facts.md`  
4. `manuscript/outline.md` 상단에 한 줄 메모로 연결한다.  
   - 예: `NotebookLM 미러: research/notebook-lm/ 참고`

이렇게 하면 채팅에서 “NotebookLM에 모은 자료 기준으로 목차 다듬어줘”라고 할 때 에이전트가 **로컬 파일**을 근거로 답할 수 있다.

## 폴더 안 제안 구조

```
notebook-lm/
  README.md          ← 이 파일
  00-index.md        ← 노트북별 링크·메모 (직접 작성)
  exports/           ← UI에서 받은보내기 (md, pdf 등)
  snippets/          ← 책에 쓸 인용·메모만 발췌
```

## 비공식 자동화 (선택)

커뮤니티에서 **NotebookLM 비공식 클라이언트**가 돌아다니나, 구글 쪽 비공개 API 변경 시 깨질 수 있다.  
자동 내려받기가 필요하면 [notebooklm-py](https://github.com/teng-lin/notebooklm-py) 등을 **별도 가상환경**에서 조사·사용하고, 결과물만 이 폴더로 복사하는 방식을 권장한다.

## Git에 올릴 때

- 저작권·개인정보가 있는 원본은 **공개 저장소에 커밋하지 말 것**.  
- 필요하면 `.gitignore`에 `exports/*.pdf` 등을 추가해 로컬에만 두기.
