from sanic import Sanic, response
from .views import SearchView, BookingView
from .exceptions import ValidationException


app = Sanic("vitrina-service")


# Search endpoint (GET, POST)
app.add_route(SearchView.as_view(), "/search")


# Booking endpoint (GET, POST)
app.add_route(BookingView.as_view(), "/booking")


@app.exception(ValidationException)
async def ignore_404s(request, e: ValidationException):
    return response.json({"detail": 
    {"msg": str(e), "field": e.extra}}, status=e.status_code)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
