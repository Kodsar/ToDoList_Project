from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    """Allowed status values for a task."""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Return True if value is one of the allowed statuses."""
        try:
            cls(value)
            return True
        except ValueError:
            return False


@dataclass
class Task:
    """Represents a single task inside a project."""

    id: int
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Project:
    """Represents a project that groups multiple tasks."""

    id: int
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    tasks: list[Task] = field(default_factory=list)
