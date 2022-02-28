import asyncio
import httpx
import json
import xmltodict
import sanic.response as response
from sanic.exceptions import SanicException
from datetime import date
from .exceptions import ValidationException


REDIS_KEY_EXPIRE = 1200
PROVIDER_TIMEOUT = 30
PROVIDERS = ['Amadeus', 'Sabre']
PENDING = 'PENDING'
DONE = 'DONE'


async def send_search(id, req, redis):
    for provider in PROVIDERS:
        await set_status(id, PENDING, redis, provider)
        asyncio.create_task(post2api(id, req, redis, provider))


async def post2api(id, req, redis, provider):
    async with httpx.AsyncClient() as client:
        req['provider'] = provider
        resp = None
        try:
            resp = await client.post(
                "https://avia-api.k8s-test.aviata.team/offers/search", 
                json=req, 
                timeout=PROVIDER_TIMEOUT)
            for item in resp.json()['items']:
                offer_id = item["id"]
                async with redis.pipeline(transaction=True) as pipe:
                    await pipe.lpush(f'vitrina.search:{id}', json.dumps(item))\
                        .set(f'vitrina.search:{offer_id}', json.dumps(item), ex=REDIS_KEY_EXPIRE)\
                        .expire(f'vitrina.search:{id}', REDIS_KEY_EXPIRE).execute()
        finally:
            await set_status(id, DONE, redis, provider)


async def set_status(id, status, redis, provider):
    await redis.set(f"vitrina.search:{provider}:STATUS:{id}", status, ex=REDIS_KEY_EXPIRE)


async def get_provider_status(id, redis, provider):
    return await redis.get(f"vitrina.search:{provider}:STATUS:{id}")


async def get_status(id, redis):
    statuses = await asyncio.gather(*(get_provider_status(id, redis, p) for p in PROVIDERS))
    return 'DONE' if set(statuses) == {'DONE'} else 'PENDING'


async def get_list(redis, id):
    offers = await redis.lrange(f'vitrina.search:{id}', 0, -1)
    return [json.loads(offer) for offer in offers]


async def get(redis, id):
    return await redis.get(f'vitrina.search:{id}')


async def rates_api(d):
    try:
        dt = date.fromisoformat(d)
    except Exception as e:
        raise SanicException(str(e))
    if dt > date.today():
        raise ValidationException("Дата должна быть раньше или равна сегодняшней")
    else:
        dt = date.today()
    async with httpx.AsyncClient() as client:
        url = f"https://www.nationalbank.kz/rss/get_rates.cfm?fdate={dt.strftime('%d.%m.%Y')}"
        resp = await client.get(url)
        if resp.status_code != 200:
            raise SanicException("Не удалось получить данные от провайдера")
        xml = xmltodict.parse(resp.text)
        rates = {rate['title']: rate['description'] for rate in xml['rates']['item']}
        return response.json({
        'date': dt.isoformat(),
        'rates': rates
        })
