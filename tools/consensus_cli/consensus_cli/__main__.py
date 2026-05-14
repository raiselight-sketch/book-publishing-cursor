"""CLI: multi-model consensus (Gemini, OpenAI, Claude, Ollama)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from consensus_cli.engine import run_consensus

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


def _load_dotenv() -> None:
    here = Path(__file__).resolve().parent.parent
    load_dotenv(here / ".env")
    load_dotenv(Path.cwd() / ".env")


def _parse_providers(s: str | None) -> set[str] | None:
    if not s:
        return None
    parts = {p.strip().lower() for p in s.split(",") if p.strip()}
    allowed = {"gemini", "openai", "anthropic", "ollama"}
    bad = parts - allowed
    if bad:
        raise typer.BadParameter(f"unknown providers: {bad}; allowed: {allowed}")
    return parts


@app.command()
def run(
    prompt: str | None = typer.Argument(None, help="한 줄 질문/지시 (없으면 stdin)"),
    prompt_file: Path | None = typer.Option(
        None, "--prompt-file", "-f", help="프롬프트 파일 (UTF-8)"
    ),
    providers: str | None = typer.Option(
        None,
        "--providers",
        "-p",
        help="쉼표 구분: gemini,openai,anthropic,ollama (기본: 키 있는 것 전부)",
    ),
    json_out: Path | None = typer.Option(
        None, "--json-out", help="전체 라운드 결과를 JSON 파일로 저장"
    ),
    text_out: Path | None = typer.Option(
        None, "--text-out", help="최종 합의 텍스트만 저장"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="최종 텍스트만 stdout"),
    skip_vote: bool = typer.Option(
        False,
        "--skip-vote",
        help="3차 투표 생략 (바로 중재자가 최종 선택)",
    ),
) -> None:
    """여러 LLM이 초안→상호 통합→투표로 최종안을 고릅니다."""
    _load_dotenv()
    if prompt_file:
        user = prompt_file.read_text(encoding="utf-8").strip()
    elif prompt:
        user = prompt.strip()
    else:
        user = sys.stdin.read().strip()
    if not user:
        raise typer.BadParameter("프롬프트가 비었습니다.")

    prov = _parse_providers(providers)
    result = run_consensus(user, prov, skip_vote=skip_vote, verbose=not quiet)

    if json_out:
        # drop raw huge if needed - keep round2 raw truncated? For now keep all
        serializable = {
            k: v
            for k, v in result.items()
            if k != "round2"
        }
        r2_compact = {}
        for key, data in result.get("round2", {}).items():
            r2_compact[key] = {
                "integrated_final": data.get("integrated_final"),
                "candidate_scores": data.get("candidate_scores"),
                "parsed_ok": bool(data.get("parsed")),
            }
        serializable["round2_summary"] = r2_compact
        json_out.write_text(
            json.dumps(serializable, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    final = result["final_text"]
    if text_out:
        text_out.write_text(final, encoding="utf-8")

    if quiet:
        print(final)
    else:
        console.rule("[bold green]최종 합의[/bold green]")
        console.print(Panel(final, title=result.get("final_source", "")))
        console.print(
            f"[dim]라운드3 표: {result.get('round3_votes')} / 집계: {result.get('vote_tally')}[/dim]"
        )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
