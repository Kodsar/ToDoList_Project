from __future__ import annotations

import os
from dataclasses import dataclass

try:
    # pip install python-dotenv  OR  poetry add python-dotenv
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    """Application-level configuration values loaded from environment."""

    project_max: int
    task_max: int


def _load_dotenv_if_available() -> None:
    """Load .env file if python-dotenv is installed."""
    if load_dotenv is not None:
        load_dotenv()


def get_settings() -> Settings:
    """
    Load settings from environment variables.

    Defaults are used when env variables are missing, so the app
    still works out-of-the-box in a dev environment.
    """
    _load_dotenv_if_available()
    project_max = int(os.getenv("PROJECT_OF_NUMBER_MAX", "5"))
    task_max = int(os.getenv("TASK_OF_NUMBER_MAX", "20"))
    return Settings(project_max=project_max, task_max=task_max)
