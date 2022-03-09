import datetime
import xmltodict
import httpx


REDIS_RATES_EXPIRE = 60 * 60 * 24


# Rates api and redis operations
async def rates_api(date, redis):
    dt = datetime.date.fromisoformat(date)
    async with httpx.AsyncClient() as client:
        url = f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={dt.strftime("%d.%m.%Y")}'
        resp = await client.get(url)
        xml = xmltodict.parse(resp.text)
        rates = {rate['title']: rate['description'] for rate in xml['rates']['item']}
        rates['date'] = date
        rates['KZT'] = 1.0
        async with redis.pipeline(transaction=True) as pipe:
            await pipe.hset('vitrina.service:currency', mapping=rates)\
                .expire('vitrina.service:currency', REDIS_RATES_EXPIRE)\
                .execute()
        print('rates_api done', datetime.date.isoformat(datetime.date.today()))


async def get_rates(redis):
    return await redis.hgetall('vitrina.service:currency')
