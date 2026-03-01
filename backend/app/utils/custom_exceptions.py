class DomainException(Exception):
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundException(DomainException):
    pass


class ValidationException(DomainException):
    pass


class ConflictException(DomainException):
    pass


class UnauthorizedException(DomainException):
    pass


class ForbiddenException(DomainException):
    pass


class InternalServerException(DomainException):
    pass


class UserAlreadyExistsException(ConflictException):
    pass


class IntegrityErrorException(InternalServerException):
    pass


class UserNotFoundException(NotFoundException):
    pass


class TaskNotFoundException(NotFoundException):
    pass


class PriorityNotFoundException(NotFoundException):
    pass


class StatusNotFoundException(NotFoundException):
    pass
