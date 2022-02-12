from .exceptions import ValidationException


# Обязательные корневые параметры POST /search
SEARCH_REQUIRED = {"provider", "cabin", "origin", "destination", "dep_at", "adults", "currency"}
# Обязательные корневые параметры POST /booking
BOOKING_REQUIRED = {"offer_id", "phone", "email", "passengers"}
# Обязательные параметры "passengers" POST /booking
BOOKING_REQUIRED_PASSENGERS = {"gender", "type", "first_name", "last_name", "date_of_birth", "citizenship", "document"}
# Обязательные параметры "document" POST /search
BOOKING_REQUIRED_DOCUMENT = {"number", "expires_at", "iin"}


# Общий валидатор параметров запроса
class Validator():

    def __init__(self, req):
        self.req = req
        self.__requiredRoot = set()

    # Валидация общих параметров
    def _required_validation(self, params, required: set):
        # Делал через тип "сет", чтобы не использовать циклы
        params = set(params)
        if not required.issubset(params):
            raise ValidationException("Недостаточно параметров")

    # Проверка на тип параметра, должен быть список
    def _islist_validation(self, param, param_name):
        if type(param) != list:
            raise ValidationException("Отсутствует массив", extra=param_name)

    # Валидация параметров внутри списка
    def _list_validation(self, params, required: set):
        for param in params:
            self._required_validation(param.keys(), required)

    # Проверка на тип параметра, должен быть словарь
    def _isdict_validation(self, param, param_name):
        if type(param) != dict:
            raise ValidationException("Отсутствует словарь", extra=param_name)


# Валидатор эндпоинта /search (child class of Validator)
class SearchValidator(Validator):

    def __init__(self, req):
        Validator.__init__(self, req)

    def validate(self):
        # Валидация корневых параметров
        self._required_validation(self.req.keys(), SEARCH_REQUIRED)


# Валидатор эндпоинта /booking (child class of Validator)
class BookingValidator(Validator):

    def __init__(self, req):
        Validator.__init__(self, req)

    def validate(self):
        # Валидация корневых параметров
        self._required_validation(self.req.keys(), BOOKING_REQUIRED)
        # Валидация на предмет списка "passengers"
        self._islist_validation(self.req["passengers"], "passengers")
        # Валидация внутри списка "passengers"
        self._list_validation(self.req["passengers"], BOOKING_REQUIRED_PASSENGERS)
        for passenger in self.req["passengers"]:
            # Валидация поля "document" внутри списка "passengers"
            self._isdict_validation(passenger["document"], "document")
            self._required_validation(passenger["document"], BOOKING_REQUIRED_DOCUMENT)
