from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    openai: str
    anthropic: str
    gemini: str
    ollama: str
    arbiter: str | None


def load_model_config() -> ModelConfig:
    return ModelConfig(
        openai=os.environ.get("CONSENSUS_MODEL_OPENAI", "gpt-4o"),
        anthropic=os.environ.get(
            "CONSENSUS_MODEL_ANTHROPIC", "anthropic/claude-3-5-sonnet-20241022"
        ),
        gemini=os.environ.get("CONSENSUS_MODEL_GEMINI", "gemini/gemini-2.0-flash"),
        ollama=os.environ.get("CONSENSUS_MODEL_OLLAMA", "ollama/gemma3:4b"),
        arbiter=os.environ.get("CONSENSUS_ARBITER_MODEL") or None,
    )


def arbiter_model(cfg: ModelConfig) -> str:
    return cfg.arbiter or cfg.anthropic
