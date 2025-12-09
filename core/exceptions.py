"""Custom exception types for the ToDo list domain."""


class DomainError(Exception):
    """Base class for domain / business-logic errors."""


class NotFoundError(DomainError):
    """Raised when an entity (project or task) is not found."""


class ValidationError(DomainError):
    """Raised when user input does not satisfy business rules."""
