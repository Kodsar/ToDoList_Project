from __future__ import annotations

from datetime import datetime
from typing import Optional

from .exceptions import DomainError, NotFoundError, ValidationError
from .models import Task, Project
from .services import InMemoryDatabase, ProjectService, TaskService


DATE_FORMAT = "%Y-%m-%d"


def _input_multiline(prompt: str) -> str:
    """
    Read multi-line text from the user and flatten it into a single string.

    The user finishes input by entering an empty line.
    """
    print(prompt)
    print("(Enter an empty line to finish)")
    lines: list[str] = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        lines.append(line)
    return " ".join(lines)


def _parse_date(value: str) -> Optional[datetime]:
    """Parse a date string in DATE_FORMAT or return None if empty."""
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValidationError(f"Invalid date format. Expected: {DATE_FORMAT}")


def _print_project(project: Project) -> None:
    """Pretty-print a project to the console."""
    print(f"[{project.id}] Name: {project.name}")
    print(f"    Description: {project.description}")
    print(f"    Created at:  {project.created_at}")
    print("-" * 60)


def _print_task(task: Task) -> None:
    """Pretty-print a task to the console."""
    print(f"[{task.id}] Title: {task.title}")
    print(f"    Status:   {task.status.value}")
    print(f"    Deadline: {task.deadline if task.deadline else '-'}")
    print(f"    Description: {task.description}")
    print(f"    Created at:  {task.created_at}")
    print("-" * 60)


def run_cli() -> None:
    """
    Main interactive CLI loop.

    This is the only layer that talks to the user directly.
    """
    db = InMemoryDatabase()
    project_service = ProjectService(db)
    task_service = TaskService(db)

    while True:
        print("\n===== ToDo List – Phase 1 (In-Memory) =====")
        print("1) Create project")
        print("2) Edit project")
        print("3) Delete project")
        print("4) List all projects")
        print("5) Add task to project")
        print("6) Change task status")
        print("7) Edit task")
        print("8) Delete task")
        print("9) List all tasks of a project")
        print("0) Exit")
        choice = input("Your choice: ").strip()

        try:
            if choice == "1":
                _handle_create_project(project_service)
            elif choice == "2":
                _handle_edit_project(project_service)
            elif choice == "3":
                _handle_delete_project(project_service)
            elif choice == "4":
                _handle_list_projects(project_service)
            elif choice == "5":
                _handle_add_task(task_service)
            elif choice == "6":
                _handle_change_task_status(task_service)
            elif choice == "7":
                _handle_edit_task(task_service)
            elif choice == "8":
                _handle_delete_task(task_service)
            elif choice == "9":
                _handle_list_tasks(task_service)
            elif choice == "0":
                print("Exiting application. Bye 👋")
                break
            else:
                print("Invalid menu option. Please try again.")
        except DomainError as e:
            # Known, user-facing errors (validation, not found, etc.)
            print(f"[Error] {e}")
        except Exception as e:  # pragma: no cover - debugging helper
            print(f"[Unexpected error] {e}")


# ---------- Handlers for each menu action ----------


def _handle_create_project(project_service: ProjectService) -> None:
    name = _input_multiline("Enter project name:")
    description = _input_multiline("Enter project description:")
    project = project_service.create_project(name=name, description=description)
    print(f"✅ Project created with id {project.id}.")


def _handle_edit_project(project_service: ProjectService) -> None:
    project_id = int(input("Enter project id to edit: ").strip())
    new_name = _input_multiline("Enter new project name:")
    new_description = _input_multiline("Enter new project description:")
    project = project_service.edit_project(
        project_id=project_id,
        new_name=new_name,
        new_description=new_description,
    )
    print(f"✅ Project {project.id} updated successfully.")


def _handle_delete_project(project_service: ProjectService) -> None:
    project_id = int(input("Enter project id to delete: ").strip())
    project_service.delete_project(project_id)
    print("✅ Project and all its tasks have been deleted (cascade delete).")


def _handle_list_projects(project_service: ProjectService) -> None:
    projects = project_service.list_projects()
    if not projects:
        print("There are no projects yet.")
        return
    print("\nProjects:")
    print("-" * 60)
    for project in projects:
        _print_project(project)


def _handle_add_task(task_service: TaskService) -> None:
    project_id = int(input("Enter project id: ").strip())
    title = _input_multiline("Enter task title:")
    description = _input_multiline("Enter task description:")
    status = input("Status (todo/doing/done) [default: todo]: ").strip() or "todo"
    deadline_str = input(f"Deadline ({DATE_FORMAT}) or leave empty: ").strip()
    deadline = _parse_date(deadline_str) if deadline_str else None

    task = task_service.add_task(
        project_id=project_id,
        title=title,
        description=description,
        status=status,
        deadline=deadline,
    )
    print(f"✅ Task created with id {task.id} in project {project_id}.")


def _handle_change_task_status(task_service: TaskService) -> None:
    project_id = int(input("Enter project id: ").strip())
    task_id = int(input("Enter task id: ").strip())
    new_status = input("New status (todo/doing/done): ").strip()
    task = task_service.change_task_status(project_id, task_id, new_status)
    print(f"✅ Task {task.id} status changed to '{task.status.value}'.")


def _handle_edit_task(task_service: TaskService) -> None:
    project_id = int(input("Enter project id: ").strip())
    task_id = int(input("Enter task id: ").strip())

    print("Leave a field empty if you do not want to change it.")

    new_title = _input_multiline("New title (or empty to keep current):")
    if not new_title.strip():
        new_title = None

    new_description = _input_multiline(
        "New description (or empty to keep current):"
    )
    if not new_description.strip():
        new_description = None

    new_status_raw = input(
        "New status (todo/doing/done) or empty to keep current: "
    ).strip()
    new_status = new_status_raw or None

    new_deadline_raw = input(
        f"New deadline ({DATE_FORMAT}) or empty to keep current: "
    ).strip()
    new_deadline = _parse_date(new_deadline_raw) if new_deadline_raw else None

    task = task_service.edit_task(
        project_id=project_id,
        task_id=task_id,
        new_title=new_title,
        new_description=new_description,
        new_status=new_status,
        new_deadline=new_deadline,
    )
    print(f"✅ Task {task.id} updated successfully.")


def _handle_delete_task(task_service: TaskService) -> None:
    project_id = int(input("Enter project id: ").strip())
    task_id = int(input("Enter task id: ").strip())
    task_service.delete_task(project_id, task_id)
    print("✅ Task deleted successfully.")


def _handle_list_tasks(task_service: TaskService) -> None:
    project_id = int(input("Enter project id: ").strip())
    try:
        tasks = task_service.list_tasks_for_project(project_id)
    except NotFoundError as exc:
        print(exc)
        return

    if not tasks:
        print("This project has no tasks.")
        return

    print(f"\nTasks for project {project_id}:")
    print("-" * 60)
    for task in tasks:
        _print_task(task)
