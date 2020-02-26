from uuid import uuid4

import settings
from .dataclassess import FileData
from .handlers import FileHandlerFactory


async def upload_file(file: FileData, redis_storage, file_storage):
    file_handler = FileHandlerFactory().create_file_handler(file)
    file_data = file_handler.get_file_data()
    file_handler.process_file()

    await file_handler.save(file_storage)

    guid = uuid4()
    key = str(guid)

    file_data.update({'id': key})

    await redis_storage.save('{}:{}'.format(settings.REDIS_KEY_PREFIX, key), file_data)

    return file_data
