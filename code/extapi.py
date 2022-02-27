import asyncio
import httpx
import json
from sanic.exceptions import NotFound


REDIS_KEY_EXPIRE = 1200
PROVIDER_TIMEOUT = 30


async def send(id, req, redis):
    for provider in ["Amadeus", "Sabre"]:
        asyncio.create_task(post2api(id, req, redis, provider))
    return id


async def post2api(id, req, redis, provider):
    async with httpx.AsyncClient() as client:
        req["provider"] = provider
        await set_status(id, "PENDING", redis, provider)
        resp = None
        try:
            resp = await client.post(
                "https://avia-api.k8s-test.aviata.team/offers/search", 
                json=req, 
                timeout=PROVIDER_TIMEOUT
                )
        except httpx.TimeoutException as te:
            await set_status(id, "DONE", redis, provider)
        finally:
            resp = resp.json()
            await set_status(id, "DONE", redis, provider)
        for item in resp["items"]:
            search_id , *rest = item
            search_id = item[search_id]
            key_id = f"vitrina.search:{id}:{search_id}"
            rest_temp = dict()
            for r in rest:
                rest_temp[r] = item[r]
            await redis.set(key_id, json.dumps(rest_temp), ex=REDIS_KEY_EXPIRE)


async def set_status(id, status, redis, provider):
    await redis.set(f"vitrina.search:{provider}:STATUS:{id}", status, ex=REDIS_KEY_EXPIRE)


async def get_provider_status(id, redis, provider):
    return await redis.get(f"vitrina.search:{provider}:STATUS:{id}")


async def get_status(id, redis):
    statuses = {"Amadeus": "", "Sabre": ""}
    for provider in statuses:
        statuses[provider] = await get_provider_status(id, redis, provider)
    if (statuses["Amadeus"] == "DONE") and (statuses["Sabre"] == "DONE"):
        return "DONE"
    else:
        return "PENDING"


async def info_keys(redis):
        key_count = await redis.info(section="Keyspace")
        if len(key_count) > 0:
            return key_count["db0"]["keys"]
        else:
            raise NotFound("Записей не найдено")


async def scan(redis, match):
    key_count = await info_keys(redis)
    n, items = await redis.scan(0, match=match, count=key_count)
    if len(items) > 0:
        return items
    else:
        raise NotFound("Записей не найдено")


async def get(redis, id):
        result = await redis.get(id)
        if result != None:
            return result
        else:
            raise NotFound("Записей не найдено")