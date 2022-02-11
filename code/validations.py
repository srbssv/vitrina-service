from .exceptions import ValidationException


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
        # Обязательные корневые параметры
        self.__requiredRoot = { "provider", "cabin", "origin", \
             "destination", "dep_at", "adults", "currency" }

    def validate(self):
        # Валидация корневых параметров
        self._required_validation(self.req.keys(), self.__requiredRoot)


# Валидатор эндпоинта /booking (child class of Validator)
class BookingValidator(Validator):

    def __init__(self, req):
        Validator.__init__(self, req)
        # Обязательные корневые параметры
        self.__requiredRoot = { "offer_id", "phone", "email", "passengers" }
        # Обязательные параметры поля "passengers"
        self.__requiredPassengers = { "gender", "type", "first_name", \
             "last_name", "date_of_birth", "citizenship", "document" }
        # Обязательные параметры поля "document"
        self.__requiredDocument = { "number", "expires_at", "iin" }

    def validate(self):
        # Валидация корневых параметров
        self._required_validation(self.req.keys(), self.__requiredRoot)
        # Валидация на предмет списка "passengers"
        self._islist_validation(self.req["passengers"], "passengers")
        # Валидация внутри списка "passengers"
        self._list_validation(self.req["passengers"], self.__requiredPassengers)
        for passenger in self.req["passengers"]:
            # Валидация поля "document" внутри списка "passengers"
            self._isdict_validation(passenger["document"], "document")
            self._required_validation(passenger["document"], self.__requiredDocument)

