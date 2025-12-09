# ToDo List — Phase 1 (In-Memory, Layered Architecture, Python OOP)

A clean, modular, and extensible ToDo List application built using **Python**, following:

* Object-Oriented Programming
* Three-layer architecture (Core / Storage / CLI)
* Separation of Concerns + Dependency Injection
* PEP8 coding conventions + full type hints
* In-Memory Repository (Phase 1 requirement)

This project is implemented strictly based on the course specification.

---

## 📁 Project Structure

```
todo_list/
├── main.py
├── .env
├── .env.example
├── pyproject.toml
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── models.py
│   └── services.py
│
├── storage/
│   ├── __init__.py
│   └── memory_storage.py
│
└── cli/
    ├── __init__.py
    └── interface.py
```

---

## Architecture Overview

The application uses **three distinct layers**:

```
[ CLI Layer ] → interacts with user
        ↓
[ Core Layer ] → business rules & validations
        ↓
[ Storage Layer ] → data access (In-Memory)
```

### Key principles:

* CLI → Core → Storage (one-direction flow)
* Core depends on Storage via **Dependency Injection**
* Zero backward dependencies (Storage never touches Core or CLI)
* Easy to replace UI or Storage layers without changing business logic

---

## Features

### ✔ Project Features

* Create project

  * Name ≥ 30 words
  * Description ≥ 150 words
  * Unique name
  * Limit based on `.env`
* Edit project
* Delete project (cascade: tasks removed automatically)
* List all projects (sorted by creation time)

### ✔ Task Features

* Add task

  * Title ≥ 30 words
  * Description ≥ 150 words
  * Status: `todo`, `doing`, `done`
  * Optional deadline (`YYYY-MM-DD`)
  * Max tasks per project (from `.env`)
* Edit task
* Change status
* Delete task
* List all tasks of a project

### ✔ Error Handling

Custom domain exceptions:

* `DomainError`
* `NotFoundError`
* `ValidationError`

CLI converts these into friendly messages.

---

## ⚙️ Environment Variables

Copy `.env.example` → `.env` and fill:

```
PROJECT_OF_NUMBER_MAX=5
TASK_OF_NUMBER_MAX=20
```

Loaded via `core/config.py`.

---

## ▶️ Running the Application

### Option 1 — Python directly

```bash
pip install python-dotenv
python main.py
```

### Option 2 — Poetry

```bash
poetry install
poetry run python main.py
```

---

## 📄 File-by-File Explanation

### 🟦 main.py

Entry point of the application.
Simply calls `run_cli()` from the CLI layer.

---

### 🟩 core/config.py

Loads settings from environment:

* Uses `Settings` dataclass
* Fallback values if `.env` is missing
* Keeps business layer free from hardcoded numbers

---

### 🟥 core/exceptions.py

Domain-specific exception classes:

* `DomainError` (base)
* `NotFoundError` (entity missing)
* `ValidationError` (invalid input)

Used heavily in services and handled by CLI.

---

### 🟪 core/models.py

Domain models:

* `Project`
* `Task`
* `TaskStatus` (Enum)

Stores *data only*—no business logic.

---

### 🟫 core/services.py

Central business logic:

* Validates projects/tasks
* Enforces limits and rules
* CRUD for projects and tasks
* Cascade delete
* Uses storage via Dependency Injection
* Completely independent of CLI or storage implementation

---

### 🟧 storage/memory_storage.py

Simple In-Memory repository:

* Stores all `Project` objects
* Each project stores its own tasks
* Generates unique project/task IDs
* Contains **no** validation or business rules

Can be replaced by SQLite, JSON, PostgreSQL, etc.

---

### 🟨 cli/interface.py

Interactive command-line UI:

* Shows menu
* Reads input
* Calls core services
* Prints results
* Catches domain exceptions

Contains **no business rules**, only user interaction.

---

## Testing Strategy (Recommended)

* Unit tests for `core/services.py`
* Fake/mocked storage for isolation
* No need to test CLI

Recommended tools:

* `pytest`
* `pytest-cov`

---

## Future Improvements

Because of the clean layering:

### Storage Upgrades

* SQLite repository
* JSON-file storage
* Full database backend

### API Layer

* FastAPI-based REST API (in `api/` folder)

### UI Improvements

* Tkinter GUI
* React or web-based UI

### Persistent Mode

Replace InMemoryDatabase without modifying core logic.

---

## Coding Standards

This project follows:

* PEP8
* 4-space indentation
* snake_case naming
* PascalCase for classes
* UPPER_SNAKE_CASE for constants
* Extensive type hints
* SRP (Single Responsibility Principle)
* No business logic in CLI or storage
* Clean error handling with custom exceptions

---

## Conclusion

This project implements **Phase 1** of the ToDo system with:

* Strong architecture
* Clean & modular code
* Full separation of concerns
* Clear business rules
* Extendable structure

Perfectly ready for future phases such as database integration, API development, and automated testing.
