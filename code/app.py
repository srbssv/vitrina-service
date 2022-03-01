from sanic import Sanic, response
import json
from sanic.exceptions import NotFound, SanicException
#import asyncpg
import aioredis
from .data import bookingResponse1, bookingResponse2
from .validations import BookingValidator
from .exceptions import ValidationException
from .settings import VitrinaConfig
from .extapi import send_search, get_status, rates_api, get_list, get
import uuid
#from apscheduler.schedulers.asyncio import AsyncIOScheduler


app = Sanic('vitrina-service', config=VitrinaConfig())


@app.listener('before_server_start')
async def init_before(app, loop):
    #app.ctx.db_pool = await asyncpg.create_pool(dsn=app.config.DATABASE_URL)
    app.ctx.redis = await aioredis.from_url(app.config.REDIS_URL, decode_responses=True, max_connections=50)


@app.listener('after_server_stop')
async def cleanup(app, loop):
    await app.ctx.redis.close()


@app.post('/search')
async def post_search(request):
    req = request.json
    id = str(uuid.uuid4())
    await send_search(id, req, app.ctx.redis)
    return response.json({'id':id})


# Search endpoint (GET, POST)
@app.get('/search/<search_id>')
async def get_search(request, search_id):
    status = await get_status(search_id, app.ctx.redis)
    if not status:
        raise NotFound('Поиск с таким id не найден!')
    offers = await get_list(search_id, app.ctx.redis)
    return response.json({
        'search_id': search_id,
        'status': status,
        'items': offers
        })


@app.get('/offers/<offer_id>')
async def get_offer(request, offer_id):
    offer = await get(offer_id, app.ctx.redis)
    if not offer:
        raise NotFound('Оффер с таким id не найден!')
    return response.json({'pepsi': json.loads(offer)})


# Booking endpoint (GET, POST)
@app.get('/booking')
async def get_booking(request):
    return response.json(bookingResponse1)


@app.post('/booking')
async def post_booking(request):
    req = request.json
    # Валидация обязательных параметров
    v = BookingValidator(req)
    return response.json(bookingResponse2)


@app.get('/get_rates')
async def get_rates(request):
    date = request.args.get('date')
    return await rates_api(date)


@app.exception(ValidationException)
async def validation_handler(request, e: ValidationException):
    return response.json(
            {
                'detail': {
                    'msg': str(e),
                    'field': e.extra
                }
            },
            status=e.status_code)


@app.exception(NotFound)
async def notfound_handler(request, e: NotFound):
    return response.json(
        {
            'details': [
                {
                    'msg': str(e)
                }
            ]
        }
    )


@app.exception(SanicException)
async def nexception_handler(request, e: SanicException):
    return response.json(
        {
            'details': [
                {
                    'msg': str(e)
                }
            ]
        }
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=app.config.DEBUG)
