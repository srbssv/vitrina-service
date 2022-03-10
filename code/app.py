from sanic import Sanic, response
import json
from sanic.exceptions import NotFound, SanicException
import asyncpg
import aioredis
from .settings import VitrinaConfig
from . import extapi
from . import rates
import uuid
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


app = Sanic('vitrina-service', config=VitrinaConfig())


@app.listener('before_server_start')
async def init_before(app, loop):
    app.ctx.redis = await aioredis.from_url(
            app.config.REDIS_URL, decode_responses=True, max_connections=50
        )
    app.ctx.db_pool = await asyncpg.create_pool(dsn=app.config.DATABASE_URL)


@app.listener('after_server_start')
async def init_after(app, loop):
    app.ctx.scheduler = AsyncIOScheduler()
    app.ctx.scheduler.add_job(
        rates.rates_api,
        'cron',
        hour=6,
        minute=0,
        second=0,
        args=(datetime.date.isoformat(datetime.date.today()), app.ctx.redis))
    app.ctx.scheduler.start()


@app.listener('after_server_stop')
async def cleanup(app, loop):
    await app.ctx.redis.close()
    app.ctx.scheduler.shutdown()


# Search endpoint (GET, POST)
@app.post('/search')
async def post_search(request):
    req = request.json
    id = str(uuid.uuid4())
    all_rates = await rates.rates_api(
        datetime.date.isoformat(datetime.date.today()),
        app.ctx.redis)
    await extapi.send_search(id, req, app.ctx.redis, req['currency'], all_rates)
    return response.json({'id': id})


@app.get('/search/<search_id>')
async def get_search(request, search_id):
    status = await extapi.get_status(search_id, app.ctx.redis)
    if not status:
        raise NotFound('Поиск с таким id не найден!')

    offers = await extapi.get_search_list(search_id, app.ctx.redis)

    return response.json({
        'search_id': search_id,
        'status': status,
        'items': offers
        })


# Offer endpoint (GET, POST)
@app.get('/offers/<offer_id>')
async def get_offer(request, offer_id):
    offer = await extapi.get_offer_value(offer_id, app.ctx.redis)
    if not offer:
        raise NotFound('Оффер с таким id не найден!')

    return response.json(json.loads(offer))


# Booking endpoint (GET, POST)
@app.post('/booking')
async def post_booking(request):
    req = request.json
    offer = await extapi.get_offer_value(req['offer_id'], app.ctx.redis)
    if not offer:
        raise NotFound('Оффер с таким id не найден, либо истекло время запроса поиска!')

    resp = await extapi.send_booking(req, app.ctx.db_pool, app.ctx.redis)
    return response.json(resp)


@app.get('/booking/<booking_id>')
async def get_booking_query(request, booking_id):
    data = await extapi.get_booking_record(booking_id, app.ctx.db_pool)
    if not data:
        raise NotFound('Бронь не найдена')

    return response.json(data)


@app.get('/booking')
async def get_booking_list(request):
    data = await extapi.get_booking_items(request.args, app.ctx.db_pool)
    return response.json(data)


# Exception handler
@app.exception(SanicException)
async def exception_handler(request, e: SanicException):
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
    app.run(host='0.0.0.0', port=8000)
