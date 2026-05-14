from __future__ import annotations

import concurrent.futures
import os
import re
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from consensus_cli.config import ModelConfig, arbiter_model, load_model_config
from consensus_cli.jsonutil import extract_json_object
from consensus_cli.providers import complete_chat

console = Console()


@dataclass
class ProviderSpec:
    key: str
    label: str
    model: str


def build_providers(cfg: ModelConfig, use: set[str]) -> list[ProviderSpec]:
    """Return enabled providers in fixed order: gemini, openai, anthropic, ollama."""
    candidates = [
        (
            "gemini",
            "Gemini",
            cfg.gemini,
            "gemini" in use and bool(os.environ.get("GEMINI_API_KEY")),
        ),
        (
            "openai",
            "ChatGPT (OpenAI)",
            cfg.openai,
            "openai" in use and bool(os.environ.get("OPENAI_API_KEY")),
        ),
        (
            "anthropic",
            "Claude (Anthropic)",
            cfg.anthropic,
            "anthropic" in use and bool(os.environ.get("ANTHROPIC_API_KEY")),
        ),
        (
            "ollama",
            "Ollama (로컬)",
            cfg.ollama,
            "ollama" in use,
        ),
    ]
    return [
        ProviderSpec(key=k, label=lab, model=m)
        for k, lab, m, ok in candidates
        if ok
    ]


def _labels(n: int) -> list[str]:
    return [chr(ord("A") + i) for i in range(n)]


def round1_drafts(
    user_prompt: str, providers: list[ProviderSpec]
) -> dict[str, str]:
    system = (
        "당신은 전문 작가·편집자입니다. 사용자 요청에 대해 "
        "완결된 답변을 한국어로 작성하세요. 불필요한 메타 설명은 줄이세요."
    )

    def one(spec: ProviderSpec) -> tuple[str, str]:
        text = complete_chat(
            spec.model,
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.45,
        )
        return spec.key, text

    out: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as ex:
        futs = [ex.submit(one, p) for p in providers]
        for fut in concurrent.futures.as_completed(futs):
            k, t = fut.result()
            out[k] = t
    return out


ROUND2_INSTRUCTION = """당신은 동료 모델들이 낸 초안을 검토하는 심사 겸 통합 편집자입니다.

[사용자 요청]
{user_prompt}

[익명 후보 답변]
{candidates}

규칙:
1) 각 후보 라벨(A,B,...)에 대해 1~5 정수 점수를 매기세요 (5가 가장 우수).
2) 각 후보에 대한 한 줄 평가를 적으세요.
3) 모순을 제거하고 강점을 합쳐 **하나의 최종 완결 답변**을 `integrated_final`에 넣으세요.

반드시 JSON 한 덩어리만 출력하세요 (코드펜스 없이 순수 JSON):
{{
  "candidate_scores": {{"A": 0, "B": 0}},
  "critiques": {{"A": "", "B": ""}},
  "integrated_final": "..."
}}
"""


def round2_integrate(
    user_prompt: str,
    providers: list[ProviderSpec],
    drafts: dict[str, str],
) -> dict[str, dict]:
    labels = _labels(len(providers))
    blocks: list[str] = []
    for lb, p in zip(labels, providers):
        body = drafts.get(p.key, "").strip()
        blocks.append(f"### 후보 {lb} ({p.label})\n{body}")
    candidates = "\n\n".join(blocks)
    user_msg = ROUND2_INSTRUCTION.format(
        user_prompt=user_prompt.strip(),
        candidates=candidates,
    )

    def one(spec: ProviderSpec) -> tuple[str, dict]:
        raw = complete_chat(
            spec.model,
            [{"role": "user", "content": user_msg}],
            temperature=0.25,
        )
        parsed = extract_json_object(raw) or {}
        return spec.key, {
            "raw": raw,
            "parsed": parsed,
            "integrated_final": str(parsed.get("integrated_final", "")).strip(),
            "candidate_scores": parsed.get("candidate_scores") or {},
        }

    out: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as ex:
        futs = [ex.submit(one, p) for p in providers]
        for fut in concurrent.futures.as_completed(futs):
            k, d = fut.result()
            out[k] = d
    return out


ROUND3_INSTRUCTION = """당신은 최종 투표자입니다. 아래는 서로 다른 시스템이 통합한 최종안 후보입니다.

[원 사용자 요청]
{user_prompt}

[통합안 후보]
{finalists}

JSON만 출력:
{{
  "winner": "T0",
  "rank_order": ["T0", "T2", "T1", "T3"],
  "reason": "한 문장 이유"
}}

winner는 반드시 T0, T1, ... 중 하나의 라벨이어야 합니다.
"""


def round3_vote(
    user_prompt: str,
    providers: list[ProviderSpec],
    integrated_by_key: dict[str, str],
) -> dict[str, str]:
    labels = [f"T{i}" for i in range(len(providers))]
    blocks = []
    for i, p in enumerate(providers):
        body = integrated_by_key.get(p.key, "").strip()
        blocks.append(f"### {labels[i]} ({p.label})\n{body}")
    finalists = "\n\n".join(blocks)
    user_msg = ROUND3_INSTRUCTION.format(
        user_prompt=user_prompt.strip(),
        finalists=finalists,
    )

    def one(spec: ProviderSpec) -> tuple[str, str]:
        raw = complete_chat(
            spec.model,
            [{"role": "user", "content": user_msg}],
            temperature=0.1,
        )
        parsed = extract_json_object(raw) or {}
        w = str(parsed.get("winner", "")).strip().upper()
        return spec.key, w

    votes: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as ex:
        futs = [ex.submit(one, p) for p in providers]
        for fut in concurrent.futures.as_completed(futs):
            k, w = fut.result()
            votes[k] = w
    return votes


def _normalize_winner_label(
    w: str, n: int
) -> str | None:
    w = w.strip().upper()
    if w.startswith("T") and len(w) >= 2 and w[1:].isdigit():
        idx = int(w[1:])
        if 0 <= idx < n:
            return f"T{idx}"
    # "T0" with extra spaces
    m = re.search(r"T(\d+)", w)
    if m:
        idx = int(m.group(1))
        if 0 <= idx < n:
            return f"T{idx}"
    return None


def tally_votes(votes: dict[str, str], n: int) -> tuple[str | None, dict[str, int]]:
    counts: dict[str, int] = {}
    for _k, w in votes.items():
        label = _normalize_winner_label(w, n)
        if not label:
            continue
        counts[label] = counts.get(label, 0) + 1
    if not counts:
        return None, counts
    best = max(counts.items(), key=lambda x: x[1])[0]
    return best, counts


def arbiter_pick(
    user_prompt: str,
    arbiter_model_name: str,
    providers: list[ProviderSpec],
    integrated_by_key: dict[str, str],
) -> str:
    labels = [f"T{i}" for i in range(len(providers))]
    parts = [f"[사용자 요청]\n{user_prompt.strip()}\n"]
    for i, p in enumerate(providers):
        parts.append(f"\n### 후보 {labels[i]} ({p.label})\n{integrated_by_key.get(p.key,'').strip()}")
    parts.append(
        "\n\n위 후보 중 **하나의 라벨**만 골라, 그 후보의 텍스트를 "
        "필요하면 최소한만 다듬어 최종 답변으로 제시하세요. "
        "먼저 한 줄로 `선택: Tn` 이라고 쓰고 빈 줄 뒤에 최종 본문을 쓰세요."
    )
    return complete_chat(
        arbiter_model_name,
        [{"role": "user", "content": "\n".join(parts)}],
        temperature=0.2,
    )


def _run_single_provider(
    user_prompt: str,
    spec: ProviderSpec,
    *,
    verbose: bool,
) -> dict:
    """제공자가 1개일 때: 합의 없이 1회 완성 응답."""
    system = (
        "당신은 전문 작가·편집자입니다. 사용자 요청에 대해 "
        "완결된 답변을 한국어로 작성하세요. 불필요한 메타 설명은 줄이세요."
    )
    if verbose:
        console.print(
            Panel.fit(
                f"• 단일 모델: {spec.label} — `{spec.model}`\n"
                "(다중 합의·투표는 생략됩니다. `-p`로 모델을 2개 이상 주면 전체 합의가 돌아갑니다.)",
                title="Consensus (단일)",
            )
        )
    text = complete_chat(
        spec.model,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.35,
    )
    text = text.strip()
    return {
        "providers": [spec.__dict__],
        "round1": {spec.key: text},
        "round2": {},
        "round3_votes": {},
        "vote_tally": {},
        "winner_label": None,
        "final_text": text,
        "final_source": f"단일 제공자 `{spec.label}`",
    }


def run_consensus(
    user_prompt: str,
    provider_filter: set[str] | None = None,
    *,
    skip_vote: bool = False,
    verbose: bool = True,
) -> dict:
    cfg = load_model_config()
    use = provider_filter or {"gemini", "openai", "anthropic", "ollama"}
    providers = build_providers(cfg, use)
    if len(providers) == 0:
        raise SystemExit(
            "활성화된 제공자가 없습니다. `.env`의 API 키와 `--providers` 옵션을 확인하세요."
        )

    if len(providers) == 1:
        return _run_single_provider(user_prompt, providers[0], verbose=verbose)

    if verbose:
        console.print(
            Panel.fit(
                "\n".join(f"• {p.label}: `{p.model}`" for p in providers),
                title="Consensus providers",
            )
        )

    drafts = round1_drafts(user_prompt, providers)
    if verbose:
        t = Table(title="Round 1 — 초안 길이(자)")
        t.add_column("모델")
        t.add_column("글자수")
        for p in providers:
            t.add_row(p.label, str(len(drafts.get(p.key, ""))))
        console.print(t)

    r2 = round2_integrate(user_prompt, providers, drafts)
    integrated_by_key = {
        k: (r2[k].get("integrated_final") or "") for k in r2
    }

    if verbose:
        console.print("[bold]Round 2[/bold] — 통합안 생성 완료 (각 모델별 integrated_final)")

    winner_label: str | None = None
    vote_counts: dict[str, int] = {}
    votes: dict[str, str] = {}

    if not skip_vote and len(providers) >= 2:
        votes = round3_vote(user_prompt, providers, integrated_by_key)
        winner_label, vote_counts = tally_votes(votes, len(providers))
        if verbose:
            console.print(f"[bold]Round 3[/bold] votes: {votes} → tally: {vote_counts}")

    chosen_text: str
    chosen_from: str

    if winner_label:
        idx = int(winner_label[1:])
        wkey = providers[idx].key
        chosen_text = integrated_by_key.get(wkey, "").strip()
        chosen_from = f"다수결 {winner_label} → {providers[idx].label}"
        if not chosen_text:
            chosen_text = arbiter_pick(
                user_prompt, arbiter_model(cfg), providers, integrated_by_key
            )
            chosen_from = "다수결 후보 비어 있음 → 중재자"
    else:
        chosen_text = arbiter_pick(
            user_prompt, arbiter_model(cfg), providers, integrated_by_key
        )
        chosen_from = f"중재 모델 `{arbiter_model(cfg)}`"

    return {
        "providers": [p.__dict__ for p in providers],
        "round1": drafts,
        "round2": r2,
        "round3_votes": votes,
        "vote_tally": vote_counts,
        "winner_label": winner_label,
        "final_text": chosen_text,
        "final_source": chosen_from,
    }
