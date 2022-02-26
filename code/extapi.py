import asyncio
import uuid
import httpx
import json
from sanic.exceptions import SanicException
from sanic import response
from aioredis import Redis

def generate_id(redis_keys):
    id = str(uuid.uuid4())
    if not id in redis_keys:
        return id
    else:
        generate_id(redis_keys)

class ExtApi:
    def __init__(self, request, app, redis: Redis, timeout, key_expire):
        self.request = request
        self.app = app
        self.redis = redis
        self.timeout = timeout
        self.key_expire = key_expire

    async def __set_status(self, id, status):
        await self.redis.set(f"vitrina.search:{id}.STATUS", status, ex=self.key_expire)

    async def __post(self, id, req, provider):
        async with httpx.AsyncClient() as client:
            req["provider"] = provider
            resp = None
            try:
                resp = await client.post(
                    "https://avia-api.k8s-test.aviata.team/offers/search", 
                    json=req, 
                    timeout=self.timeout
                    )
            except httpx.TimeoutException as te:
                resp = resp.json()
            except httpx.RequestError as re:
                print("ERROR IS ERROR IS ", str(re))
                raise SanicException(str(re))
            if resp != None:
                resp = resp.json()
                for item in resp["items"]:
                    search_id , *rest = item
                    search_id = item[search_id]
                    key_id = f"vitrina.search:{id}:{search_id}"
                    rest_temp = dict()
                    for r in rest:
                        rest_temp[r] = item[r]
                    await self.redis.set(key_id, json.dumps(rest_temp), ex=self.key_expire)
                if provider == "Sabre":
                    await self.__set_status(id, "DONE")
                    

    async def send(self):
        id = generate_id([])
        await self.__set_status(id, "PENDING")
        for provider in ["Amadeus", "Sabre"]:
            task = asyncio.create_task(self.__post(id, self.request, provider))
        return id