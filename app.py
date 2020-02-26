import asyncio

import aiohttp_cors
import uvloop
from aiohttp import web

import settings
from files.routes import routes
from middleware import error_middleware
from storage import RedisStorage, MinioStorage
from utils import get_class_by_path

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


app = web.Application(
    middlewares=[error_middleware],
    client_max_size=settings.MAX_FILE_SIZE
)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_methods=["OPTION", "POST", "GET"],
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in routes:
    cors.add(app.router.add_route(**route))


if MinioStorage.__name__ in settings.STORAGE_CLASS:
    async def create_minio_client(app):
        app['file_storage'] = MinioStorage()
        await app['file_storage'].init(loop)
        yield
    
    
    async def close_minio_client(app):
        await app['file_storage'].close()

    app.cleanup_ctx.append(create_minio_client)
    app.on_cleanup.append(close_minio_client)
else:
    app['file_storage'] = get_class_by_path(settings.STORAGE_CLASS)()


async def create_redis_pool(app):
    app['redis_storage'] = RedisStorage()
    await app['redis_storage'].init(loop)
    yield


async def close_session(app):
    await app.session.close()
    yield


async def close_redis_pool(app):
    await app['redis_storage'].close()

app.cleanup_ctx.append(create_redis_pool)
app.on_cleanup.append(close_redis_pool)


web.run_app(app, host=settings.HOST, port=settings.PORT)
