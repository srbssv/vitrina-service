import asyncio
import httpx
import json


REDIS_KEY_EXPIRE = 60 * 20
PROVIDER_TIMEOUT = 30
PROVIDERS = ['Amadeus', 'Sabre']
PENDING = 'PENDING'
DONE = 'DONE'


# Search api operations
async def send_search(id, req, redis, rate_name, all_rates):
    for provider in PROVIDERS:
        await set_status(id, PENDING, redis, provider)
        asyncio.create_task(search_api(id, req, redis, provider, rate_name, all_rates))


async def search_api(id, req, redis, provider: str, rate_name: str, all_rates):
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
                price = float(item['price']['amount']) * \
                    float(all_rates[item['price']['currency']]) / \
                    float(all_rates[rate_name])
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


async def get_search_list(id, redis):
    offers = await redis.lrange(f'vitrina.search:{id}', 0, -1)
    return [json.loads(offer) for offer in offers]


async def get_offer_value(id, redis):
    return await redis.get(f'vitrina.search:{id}')


# Booking operations
async def send_booking(req, db_pool, redis):
    return await booking_api(req, db_pool, redis)


async def booking_api(req, db_pool, redis):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://avia-api.k8s-test.aviata.team/offers/booking',
            json=req,
            timeout=PROVIDER_TIMEOUT)
        resp = resp.json()
        redis_offer = await get_offer_value(req['offer_id'], redis)

        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    'INSERT INTO booking '
                    '(id, pnr, expires_at, phone, email, offer) '
                    'VALUES ($1, $2, $3, $4, $5, $6)',
                    resp['id'],
                    resp['pnr'],
                    resp['expires_at'],
                    resp['phone'],
                    resp['email'],
                    redis_offer)

                for passenger in resp['passengers']:
                    await conn.execute(
                        'INSERT INTO passengers '
                        '(gender, type, first_name,'
                        'last_name, date_of_birth,'
                        'citizenship, document, booking_id) '
                        'VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
                        passenger['gender'],
                        passenger['type'],
                        passenger['first_name'],
                        passenger['last_name'],
                        passenger['date_of_birth'],
                        passenger['citizenship'],
                        json.dumps(passenger['document']),
                        resp['id'])
        return resp


def return_booking_list(data):
    return [return_booking_record(d) for d in data]


def return_booking_record(data):
    return {
            'id': data['id'],
            'pnr': data['pnr'],
            'expires_at': data['expires_at'],
            'phone': data['phone'],
            'email': data['email'],
            'offer': json.loads(data['offer']),
            'passengers': {
                'gender': data['gender'],
                'type': data['type'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'date_of_birth': data['date_of_birth'],
                'citizenship': data['citizenship'],
                'document': json.loads(data['document'])
            }
        }


def return_booking_items(data, page, limit, total):
    results = return_booking_list(data)
    return {
        'page': page,
        'items': results,
        'limit': limit,
        'total': total
    }


async def get_booking_record(booking, db_pool):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            data = await conn.fetchrow(
                    'SELECT * FROM booking '
                    'INNER JOIN passengers '
                    'ON passengers.booking_id=booking.id '
                    'WHERE booking.id=$1',
                    booking)
            if not data:
                return

            return return_booking_record(data)


async def get_booking_items(args, db_pool):
    # Получаем offset и limit
    page = int(args.get('page', 1))
    if page < 1:
        page = 1

    limit = int(args.get('limit', 10))
    filters = {
        'phone': args.get('phone'),
        'email': args.get('email'),
    }
    if filters['phone']:
        filters['phone'] = '+' + filters['phone'][1:]

    filters = {k: v for k, v in filters.items() if v}
    filters_str = ''
    if filters:
        filters_str = 'WHERE ' + ' AND '.join(f'{k}=\'{v}\'' for k, v in filters.items())

    sql_list = ['SELECT * FROM booking '
                'INNER JOIN passengers '
                'ON passengers.booking_id=booking.id ',
                filters_str,
                f' OFFSET {page - 1} LIMIT {limit} ']
    sql = ' '.join(sql_list)

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            data = await conn.fetch(sql)
            total = await conn.fetchval('SELECT COUNT(*) FROM booking')
            return return_booking_items(data, page, limit, total)
