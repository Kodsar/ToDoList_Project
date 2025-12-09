from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .config import get_settings
from .exceptions import NotFoundError, ValidationError
from .models import Project, Task, TaskStatus


# Word-count limits are derived from the specification.
MIN_PROJECT_NAME_WORDS = 30
MIN_PROJECT_DESCRIPTION_WORDS = 150
MIN_TASK_TITLE_WORDS = 30
MIN_TASK_DESCRIPTION_WORDS = 150


def _word_count(text: str) -> int:
    """Return the number of words in a string."""
    return len(text.split())


@dataclass
class InMemoryDatabase:
    """
    Simple in-memory storage for projects and tasks.

    In phase 1, there is no persistent storage. This class simulates
    a repository that can later be swapped with a DB implementation.
    """

    projects: list[Project] = field(default_factory=list)
    _project_id_seq: int = 0
    _task_id_seq: int = 0

    def next_project_id(self) -> int:
        """Generate the next unique project ID."""
        self._project_id_seq += 1
        return self._project_id_seq

    def next_task_id(self) -> int:
        """Generate the next unique task ID."""
        self._task_id_seq += 1
        return self._task_id_seq


class ProjectService:
    """
    Business logic for managing projects.

    This layer should not know about CLI, HTTP, or storage details.
    """

    def __init__(self, db: InMemoryDatabase) -> None:
        self._db = db
        self._settings = get_settings()

    # ---------- internal helpers ----------

    def _find_project(self, project_id: int) -> Project:
        """Return a project by ID or raise NotFoundError."""
        for project in self._db.projects:
            if project.id == project_id:
                return project
        raise NotFoundError(f"Project with id {project_id} was not found.")

    def _ensure_project_name_unique(
        self,
        name: str,
        exclude_id: Optional[int] = None,
    ) -> None:
        """
        Check that the project name is unique.

        exclude_id can be used when updating a project
        to ignore the current project's own name.
        """
        for project in self._db.projects:
            if project.name == name and (exclude_id is None or project.id != exclude_id):
                raise ValidationError("Project name must be unique.")

    def _validate_project_fields(self, name: str, description: str) -> None:
        """Validate name and description according to word-count rules."""
        if _word_count(name) < MIN_PROJECT_NAME_WORDS:
            raise ValidationError(
                f"Project name must contain at least {MIN_PROJECT_NAME_WORDS} words."
            )
        if _word_count(description) < MIN_PROJECT_DESCRIPTION_WORDS:
            raise ValidationError(
                f"Project description must contain "
                f"at least {MIN_PROJECT_DESCRIPTION_WORDS} words."
            )

    # ---------- public API ----------

    def create_project(self, name: str, description: str) -> Project:
        """
        Create a new project.

        Enforces:
        - max number of projects from settings
        - word limits
        - unique project name
        """
        if len(self._db.projects) >= self._settings.project_max:
            raise ValidationError(
                "Maximum number of projects reached (PROJECT_OF_NUMBER_MAX)."
            )

        self._validate_project_fields(name, description)
        self._ensure_project_name_unique(name)

        project = Project(
            id=self._db.next_project_id(),
            name=name,
            description=description,
        )
        self._db.projects.append(project)
        return project

    def edit_project(
        self,
        project_id: int,
        new_name: str,
        new_description: str,
    ) -> Project:
        """Update project name and description."""
        project = self._find_project(project_id)
        self._validate_project_fields(new_name, new_description)
        self._ensure_project_name_unique(new_name, exclude_id=project.id)

        project.name = new_name
        project.description = new_description
        return project

    def delete_project(self, project_id: int) -> None:
        """
        Delete a project.

        Implements cascade delete: all tasks of the project
        are removed together with the project.
        """
        self._find_project(project_id)  # ensure it exists
        self._db.projects = [
            project for project in self._db.projects if project.id != project_id
        ]

    def list_projects(self) -> list[Project]:
        """Return all projects sorted by creation time."""
        return sorted(self._db.projects, key=lambda p: p.created_at)


class TaskService:
    """
    Business logic for managing tasks within projects.
    """

    def __init__(self, db: InMemoryDatabase) -> None:
        self._db = db
        self._settings = get_settings()

    # ---------- internal helpers ----------

    def _find_project(self, project_id: int) -> Project:
        """Find a project by ID or raise NotFoundError."""
        for project in self._db.projects:
            if project.id == project_id:
                return project
        raise NotFoundError(f"Project with id {project_id} was not found.")

    def _find_task(self, project: Project, task_id: int) -> Task:
        """Find a task within a project or raise NotFoundError."""
        for task in project.tasks:
            if task.id == task_id:
                return task
        raise NotFoundError(f"Task with id {task_id} in this project was not found.")

    def _validate_task_fields(
        self,
        title: str,
        description: str,
        status: str,
        deadline: Optional[datetime],
    ) -> TaskStatus:
        """Validate task fields and return a TaskStatus instance."""
        if _word_count(title) < MIN_TASK_TITLE_WORDS:
            raise ValidationError(
                f"Task title must contain at least {MIN_TASK_TITLE_WORDS} words."
            )
        if _word_count(description) < MIN_TASK_DESCRIPTION_WORDS:
            raise ValidationError(
                f"Task description must contain "
                f"at least {MIN_TASK_DESCRIPTION_WORDS} words."
            )

        if not TaskStatus.is_valid(status):
            raise ValidationError(
                "Invalid task status. Only 'todo', 'doing', and 'done' are allowed."
            )

        # For phase 1, we assume any datetime object passed as deadline is valid.
        return TaskStatus(status)

    # ---------- public API ----------

    def add_task(
        self,
        project_id: int,
        title: str,
        description: str,
        status: str = "todo",
        deadline: Optional[datetime] = None,
    ) -> Task:
        """
        Add a new task to a project.

        Enforces:
        - max number of tasks per project from settings
        - word limits
        - valid status
        """
        project = self._find_project(project_id)

        if len(project.tasks) >= self._settings.task_max:
            raise ValidationError(
                "Maximum number of tasks reached (TASK_OF_NUMBER_MAX)."
            )

        # Default status is 'todo' when not specified.
        if status is None:
            status = "todo"

        status_enum = self._validate_task_fields(title, description, status, deadline)

        task = Task(
            id=self._db.next_task_id(),
            title=title,
            description=description,
            status=status_enum,
            deadline=deadline,
        )
        project.tasks.append(task)
        return task

    def change_task_status(
        self,
        project_id: int,
        task_id: int,
        new_status: str,
    ) -> Task:
        """Change only the status of an existing task."""
        project = self._find_project(project_id)
        task = self._find_task(project, task_id)

        if not TaskStatus.is_valid(new_status):
            raise ValidationError(
                "Invalid task status. Only 'todo', 'doing', and 'done' are allowed."
            )

        task.status = TaskStatus(new_status)
        return task

    def edit_task(
        self,
        project_id: int,
        task_id: int,
        new_title: Optional[str] = None,
        new_description: Optional[str] = None,
        new_status: Optional[str] = None,
        new_deadline: Optional[datetime] = None,
    ) -> Task:
        """
        Edit multiple fields of a task.

        If a field is None, the existing value is kept.
        """
        project = self._find_project(project_id)
        task = self._find_task(project, task_id)

        title = new_title if new_title is not None else task.title
        description = (
            new_description if new_description is not None else task.description
        )
        status_str = new_status if new_status is not None else task.status.value
        deadline = new_deadline if new_deadline is not None else task.deadline

        status_enum = self._validate_task_fields(title, description, status_str, deadline)

        task.title = title
        task.description = description
        task.status = status_enum
        task.deadline = deadline
        return task

    def delete_task(self, project_id: int, task_id: int) -> None:
        """
        Delete a task from a project.

        Raises NotFoundError if the task does not exist.
        """
        project = self._find_project(project_id)
        before = len(project.tasks)
        project.tasks = [task for task in project.tasks if task.id != task_id]
        if len(project.tasks) == before:
            raise NotFoundError(
                f"Task with id {task_id} in this project was not found."
            )

    def list_tasks_for_project(self, project_id: int) -> list[Task]:
        """Return all tasks of a project sorted by creation time."""
        project = self._find_project(project_id)
        return sorted(project.tasks, key=lambda t: t.created_at)
