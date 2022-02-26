from aioredis import Redis
from sanic.exceptions import NotFound

class RedisDb:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def __info_keys(self):
        key_count = await self.redis.info(section="Keyspace")
        if len(key_count) > 0:
            return key_count["db0"]["keys"]
        else:
            raise NotFound("Записей не найдено")

    async def scan(self, match):
        key_count = await self.__info_keys()
        n, items = await self.redis.scan(0, match=match, count=key_count)
        if len(items) > 0:
            return items
        else:
            raise NotFound("Записей не найдено")

    async def get(self, id):
        result = await self.redis.get(id)
        if result != None:
            return result
        else:
            raise NotFound("Записей не найдено")

    async def status(self, id):
        status = ""
        try:
            status = await self.get(f"vitrina.search:{id}.STATUS")
        finally:
            return status