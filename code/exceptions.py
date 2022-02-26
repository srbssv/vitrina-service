from sanic.exceptions import SanicException


class ValidationException(SanicException):
    status_code = 422
