class UserAlreadyExistsException(Exception):
    pass


class IntegrityErrorException(Exception):
    pass


class InternalServerException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class TaskNotFoundException(Exception):
    pass


class PriorityNotFoundException(Exception):
    pass
