import asyncio
import httpx
import json
import xmltodict
import datetime
from asyncpg import Pool


REDIS_KEY_EXPIRE = 60 * 20
REDIS_RATES_EXPIRE = 60 * 60 * 24
PROVIDER_TIMEOUT = 30
PROVIDERS = ['Amadeus', 'Sabre']
PENDING = 'PENDING'
DONE = 'DONE'


# Search api operations
async def send_search(id, req, redis, rate_name, rate_value):
    for provider in PROVIDERS:
        await set_status(id, PENDING, redis, provider)
        asyncio.create_task(search_api(id, req, redis, provider, rate_name, rate_value))


async def search_api(id, req, redis, provider: str, rate_name: str, rate_value: float):
    async with httpx.AsyncClient() as client:
        req['provider'] = provider
        try:
            resp = await client.post(
                'https://avia-api.k8s-test.aviata.team/offers/search', 
                json=req, 
                timeout=PROVIDER_TIMEOUT)
            for item in resp.json()['items']:
                offer_id = item['id']
                # Расчет валюты в запросе
                price = float(item['price']['amount']) / rate_value
                item['price']['amount'] = round(price, 2)
                item['price']['currency'] = rate_name
                async with redis.pipeline(transaction=True) as pipe:
                    await pipe.lpush(f'vitrina.search:{id}', json.dumps(item))\
                        .set(f'vitrina.search:{offer_id}', json.dumps(item), ex=REDIS_KEY_EXPIRE)\
                        .expire(f'vitrina.search:{id}', REDIS_KEY_EXPIRE).execute()
        finally:
            await set_status(id, DONE, redis, provider)


# Search redis operations
async def set_status(id, status, redis, provider):
    await redis.set(f'vitrina.search:{provider}:STATUS:{id}', status, ex=REDIS_KEY_EXPIRE)


async def get_provider_status(id, redis, provider):
    return await redis.get(f'vitrina.search:{provider}:STATUS:{id}')


async def get_status(id, redis):
    statuses = await asyncio.gather(*(get_provider_status(id, redis, p) for p in PROVIDERS))
    if None in statuses:
        return
    return 'DONE' if set(statuses) == {'DONE'} else 'PENDING'


async def get_list(id, redis):
    offers = await redis.lrange(f'vitrina.search:{id}', 0, -1)
    return [json.loads(offer) for offer in offers]


async def get(id, redis):
    return await redis.get(f'vitrina.search:{id}')


# Rates api and redis operations
async def rates_api(date, redis):
    dt = datetime.date.fromisoformat(date)
    async with httpx.AsyncClient() as client:
        url = f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={dt.strftime("%d.%m.%Y")}'
        resp = await client.get(url)
        xml = xmltodict.parse(resp.text)
        rates = {rate['title']:rate['description'] for rate in xml['rates']['item']}
        rates['date'] = date
        rates['KZT'] = 1.0
        async with redis.pipeline(transaction=True) as pipe:
            await pipe.hset('vitrina.service:currency', mapping=rates)\
                .expire('vitrina.service:currency', REDIS_RATES_EXPIRE)\
                    .execute()
        print('rates_api done', datetime.date.isoformat(datetime.date.today()))
            

async def get_ratevalue(name, redis):
    return await redis.hget('vitrina.service:currency', name)


async def get_ratekey(redis):
    return await redis.exists('vitrina.service:currency')


# Booking rates operations
async def send_booking(req, db_pool: Pool):
    return await booking_api(req, db_pool)
    

async def booking_api(req, db_pool: Pool):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://avia-api.k8s-test.aviata.team/offers/booking', 
            json=req, 
            timeout=PROVIDER_TIMEOUT)
        resp = resp.json()
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO booking (id, pnr, expires_at, phone, email, offer)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ''',
                    resp['id'], resp['pnr'], resp['expires_at'], 
                    resp['phone'], resp['email'], json.dumps(resp['offer'])
                )
                for passenger in resp['passengers']:
                        await conn.execute('''
                            INSERT INTO passengers (gender, type, first_name, last_name, date_of_birth,
                            citizenship, document, booking_id)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)''', 
                            passenger['gender'], passenger['type'], passenger['first_name'], 
                            passenger['last_name'], passenger['date_of_birth'], passenger['citizenship'], 
                            json.dumps(passenger['document']), resp['id']
                        )
        return resp


async def get_booking(args, db_pool: Pool):
    PASSENGERS_KEYS = ['gender', 'type', 'first_name', 'last_name', 'date_of_birth', 'citizenship', 'document']
    JSON_KEYS = ['offer', 'document']
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            if args == 'ALL':
                data = await conn.fetch('''
                    SELECT b.*, p.gender, p.type, p.first_name, p.last_name, p.date_of_birth, p.citizenship, p.document
                    FROM booking 
                    AS b INNER JOIN passengers 
                    AS p ON p.booking_id=b.id
                ''')
            else:
                data = await conn.fetch('''
                    SELECT b.*, p.gender, p.type, p.first_name, p.last_name, p.date_of_birth, p.citizenship, p.document
                    FROM booking 
                    AS b INNER JOIN passengers 
                    AS p ON p.booking_id=b.id 
                    WHERE id=$1
                ''', args)
        return [
            {
                'id': d['id'], 'pnr': d['pnr'], 'expires_at': d['expires_at'],
                'phone': d['phone'], 'email': d['email'], 'offer': json.loads(d['offer']),
                'passengers': {
                    'gender': d['gender'], 'type': d['type'], 
                    'first_name': d['first_name'], 'last_name': d['last_name'], 
                    'date_of_birth': d['date_of_birth'], 'citizenship': d['citizenship'],
                    'document': json.loads(d['document'])
                }
            }
            for d in data
        ]