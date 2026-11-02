"""Paths and settings for the backend. Tests pass their own Settings."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from app.auth import Role

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_ID = "claude-sonnet-5-5"
TOKEN_VARIABLES: dict[str, Role] = {
    "INTERVIEWER_TOKEN": "interviewer",
    "MANAGER_TOKEN": "manager",
}


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    hiring_dir: Path
    model_id: str = DEFAULT_MODEL_ID
    # Bearer token -> role. Tokens come from the environment, never from the repo.
    api_tokens: Mapping[str, Role] = field(default_factory=dict)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"


def default_settings() -> Settings:
    tokens = {
        os.environ[variable]: role
        for variable, role in TOKEN_VARIABLES.items()
        if os.environ.get(variable)
    }
    return Settings(
        data_dir=REPO_ROOT / "data", hiring_dir=REPO_ROOT / "hiring", api_tokens=tokens
    )
