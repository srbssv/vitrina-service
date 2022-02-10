from sanic.views import HTTPMethodView
from sanic.response import json
from validations import BookingValidator, SearchValidator
from exceptions import ValidationException
from data import searchResponse, offerResponse, bookingResponse1, bookingResponse2

# Класс запросов для /search
class SearchView(HTTPMethodView):

    # GET method
    async def get(self, request):
        return json(searchResponse)

    # POST method
    async def post(self, request):
        req = request.json
        # Валидация обязательных параметров
        try:
            v = SearchValidator(req)
            v.validate()
        except ValidationException as e:
            return json( {"detail": {"msg": str(e), "field": e.extra}}, status=e.status_code )
        else:
            return json({ "id": 1 })


# Класс запросов для /booking
class BookingView(HTTPMethodView):

    # GET method
    async def get(self, request):
        return json(bookingResponse1)

    # POST method
    async def post(self, request):
        req = request.json
        # Валидация обязательных параметров
        try:
            v = BookingValidator(req)
            v.validate()
        except ValidationException as e:
            return json( {"detail": {"msg": str(e), "field": e.extra}}, status=e.status_code )
        else:
            return json({bookingResponse2})