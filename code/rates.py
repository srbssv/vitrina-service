import datetime
import xmltodict
import httpx
import json


REDIS_RATES_EXPIRE = 60 * 60 * 24


# Rates api and redis operations
async def rates_api(date, redis):
    if rates := await get_rates(redis):
        return rates

    dt = datetime.date.fromisoformat(date)

    async with httpx.AsyncClient() as client:
        url = f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={dt.strftime("%d.%m.%Y")}'
        resp = await client.get(url)
        xml = xmltodict.parse(resp.text)
        rates = {rate['title']: rate['description'] for rate in xml['rates']['item']}
        rates['date'] = date
        rates['KZT'] = 1.0
        await redis.set('vitrina.service:currency', json.dumps(rates), ex=REDIS_RATES_EXPIRE)
        return rates


async def get_rates(redis):
    if not await redis.exists('vitrina.service:currency'):
        return

    return json.loads(await redis.get('vitrina.service:currency'))
