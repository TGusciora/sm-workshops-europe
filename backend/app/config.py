"""Paths and settings for the backend. Tests pass their own Settings."""

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_ID = "claude-sonnet-5-5"


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    hiring_dir: Path
    model_id: str = DEFAULT_MODEL_ID

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"


def default_settings() -> Settings:
    return Settings(data_dir=REPO_ROOT / "data", hiring_dir=REPO_ROOT / "hiring")
