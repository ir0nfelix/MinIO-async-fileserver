import json

import aiobotocore
import aioredis

import settings


class StorageBase:
    async def save(self, key, data):
        raise NotImplementedError


class MinioStorage(StorageBase):
    async def init(self, loop=None):
        endpoint_url = f'{settings.MINIO_SCHEME}://{settings.MINIO_HOST}:{settings.MINIO_PORT}'
        session = aiobotocore.get_session(loop=loop)
        self.storage = session.create_client(
            's3',
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            endpoint_url=endpoint_url,
        )

    async def close(self):
        await self.storage.close()

    async def save(self, key, data):
        await self.storage.put_object(Bucket=settings.MINIO_BUCKET_NAME, Key=key, Body=data)


class RedisStorage(StorageBase):
    async def init(self, loop=None):
        address = f'{settings.REDIS_SCHEME}://{settings.REDIS_HOST}:{settings.REDIS_PORT}'
        self.storage = await aioredis.create_redis_pool(
            address,
            db=settings.REDIS_DB,
            minsize=settings.REDIS_MINPOOL,
            maxsize=settings.REDIS_MAXPOOL,
            loop=loop
        )

    async def close(self):
        self.storage.close()
        await self.storage.wait_closed()

    async def get(self, key):
        with await self.storage as conn:
            result = await conn.get(key)
            return json.loads(result) if result else {}

    async def save(self, key, data):
        with await self.storage as conn:
            await conn.set(key, json.dumps(data), expire=settings.REDIS_EXPIRE)


class TestStorage(StorageBase):
    async def save(self, key, data):
        pass
