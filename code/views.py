from sanic.views import HTTPMethodView
from sanic.response import json
from .validations import BookingValidator, SearchValidator
from .data import searchResponse, bookingResponse1, bookingResponse2


# Класс запросов для /search
class SearchView(HTTPMethodView):

    # GET method
    async def get(self, request):
        return json(searchResponse)

    # POST method
    async def post(self, request):
        req = request.json
        # Валидация обязательных параметров
        v = SearchValidator(req)
        v.validate()
        return json(searchResponse)


# Класс запросов для /booking
class BookingView(HTTPMethodView):

    # GET method
    async def get(self, request):
        return json(bookingResponse1)

    # POST method
    async def post(self, request):
        req = request.json
        # Валидация обязательных параметров
        v = BookingValidator(req)
        v.validate()
        return json(bookingResponse2)
