import aiobotocore

import settings


class MinioStorage:
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
