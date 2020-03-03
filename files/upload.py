from uuid import uuid4

import settings
from .dataclassess import FileData
from .handlers import FileHandlerFactory


async def upload_file(file: FileData, file_storage):
    file_handler = FileHandlerFactory().create_file_handler(file)
    file_data = file_handler.get_file_data()
    file_handler.process_file()

    await file_handler.save(file_storage)

    guid = uuid4()
    key = str(guid)

    file_data.update({'id': key})
    return file_data
