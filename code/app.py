from sanic import Sanic, response
from views import SearchView, BookingView
from data import offerResponse

app = Sanic("vitrina-service")

# Alive or not
@app.get("/")
async def alive(request):
    return response.json( {"alive": "true"} )

# Offer endpoint

@app.get("/offers/<offer_id>")
async def offers(request, offer_id):
    return response.json(offerResponse)

# Search endpoint (GET, POST)
app.add_route(SearchView.as_view(), "/search")
# Booking endpoint (GET, POST)
app.add_route(BookingView.as_view(), "/booking")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
