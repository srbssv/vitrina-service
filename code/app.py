from sanic import Sanic, response
import json
from sanic.exceptions import NotFound, SanicException
#import asyncpg
import aioredis
import httpx
#from .views import SearchView, BookingView
from .data import searchResponse, bookingResponse1, bookingResponse2
from .validations import BookingValidator, SearchValidator
from .exceptions import ValidationException
from .settings import VitrinaConfig
from .extapi import ExtApi
from .db import RedisDb



app = Sanic("vitrina-service", config=VitrinaConfig())


@app.listener("before_server_start")
async def init_before(app, loop):
    #app.ctx.db_pool = await asyncpg.create_pool(dsn=app.config.DATABASE_URL)
    app.ctx.redis = await aioredis.from_url(app.config.REDIS_URL, decode_responses=True, max_connections=50)


@app.listener("after_server_stop")
async def cleanup(app, loop):
    await app.ctx.redis.close()


# Search endpoint (GET, POST)
#app.add_route(SearchView.as_view(), "/search")
@app.get("/search/<search_id>")
async def get_search(request, search_id):
    r = RedisDb(app.ctx.redis)
    items = await r.scan(f"vitrina.search:{search_id}:*")
    search_ids = [i.split(":")[2] for i in items]
    status = await r.status(search_id)
    return response.json({
        "search_id": search_id,
        "status": status,
        "items": search_ids
        })


@app.get("/offers/<offer_id>")
async def get_offer(request, offer_id):
    r = RedisDb(app.ctx.redis)
    offer = await r.scan(f"vitrina.search:*:{offer_id}")
    offer = await r.get(offer[0])
    offer = json.loads(offer)
    return response.json({
        "offer_id": offer_id,
        "items": offer
        })


@app.post("/search")
async def post_search(request):
    req = request.json
    v = SearchValidator(req)
    ext_api = ExtApi(req, app, app.ctx.redis, app.config.PROVIDER_TIMEOUT, app.config.REDIS_KEY_EXPIRE)
    ext_api_result = await ext_api.send()
    return response.json({"id":ext_api_result})


# Booking endpoint (GET, POST)
#app.add_route(BookingView.as_view(), "/booking")
@app.get("/booking")
async def get_booking(request):
    return response.json(bookingResponse1)


@app.post("/booking")
async def post_booking(request):
    req = request.json
    # Валидация обязательных параметров
    v = BookingValidator(req)
    return response.json(bookingResponse2)


@app.exception(ValidationException)
async def validation_handler(request, e: ValidationException):
    return response.json(
            {
                "detail": {
                    "msg": str(e),
                    "field": e.extra
                }
            },
            status=e.status_code)


@app.exception(NotFound)
async def notfound_handler(request, e: NotFound):
    return response.json(
        {
            "detail": [
                {
                    "msg": str(e)
                }
            ]
        }
    )


@app.exception(SanicException)
async def nexception_handler(request, e: SanicException):
    return response.json(
        {
            "detail": [
                {
                    "msg": str(e)
                }
            ]
        }
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=app.config.DEBUG)
