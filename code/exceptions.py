from sanic.exceptions import SanicException, NotFound


class ValidationException(SanicException):
    status_code = 422
    extra = ""


class NotFoundException(NotFound):
    message = "Бронь не найдена"

