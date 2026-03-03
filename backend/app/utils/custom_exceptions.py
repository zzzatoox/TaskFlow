class DomainException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"
    headers: dict | None = None

    def __init__(self, detail: str | None = None, headers: dict | None = None):
        if detail:
            self.detail = detail
        if headers:
            self.headers = headers


class NotFoundException(DomainException):
    status_code = 404
    detail = "Resource not found"


class ValidationException(DomainException):
    status_code = 422
    detail = "Validation error"


class ConflictException(DomainException):
    status_code = 409
    detail = "A conflict occured with the current state of resource"


class UnauthorizedException(DomainException):
    status_code = 401
    detail = "Could not validate credentials"


class ForbiddenException(DomainException):
    status_code = 403
    detail = "Permission denied"


class InternalServerException(DomainException):
    detail = "An unexpected error occurred on the server"


class UserAlreadyExistsException(ConflictException):
    detail = "User with this credentials already exists"


class StatusAlreadyExistsException(ConflictException):
    detail = "Status with this title already exists"


class PriorityAlreadyExistsException(ConflictException):
    detail = "Priority with this title already exists"


class IntegrityErrorException(InternalServerException):
    pass


class UserNotFoundException(NotFoundException):
    detail = "User not found"


class TaskNotFoundException(NotFoundException):
    detail = "Task not found"


class PriorityNotFoundException(NotFoundException):
    detail = "Priority not found"


class StatusNotFoundException(NotFoundException):
    detail = "Status not found"
