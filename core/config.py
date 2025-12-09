from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv  # poetry add python-dotenv
except ImportError:
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    project_max: int
    task_max: int


def _load_dotenv_if_available() -> None:
    if load_dotenv is not None:
        load_dotenv()


def get_settings() -> Settings:
    """
    مقادیر تنظیمات را از .env می‌خواند و اگر نبود مقدار پیش‌فرض می‌گذارد.
    """
    _load_dotenv_if_available()
    project_max = int(os.getenv("PROJECT_OF_NUMBER_MAX", "5"))
    task_max = int(os.getenv("TASK_OF_NUMBER_MAX", "20"))
    return Settings(project_max=project_max, task_max=task_max)
