from aiohttp import web
from aiohttp.web_exceptions import HTTPRequestEntityTooLarge
from aiohttp.web_request import FileField
from aiohttp.web_response import json_response

import settings
from decorators import authenticate
from exceptions import FileServerError, OversizeFileError
from .dataclassess import FileData
from .upload import upload_file


def index(request):
    return web.Response(body='I am File Server')


# @authenticate
async def upload(request):
    try:
        post = await request.post()
        file: FileField = post[settings.FILE_FIELD_NAME]
    except HTTPRequestEntityTooLarge:
        raise OversizeFileError()
    except:
        raise FileServerError('Файл не был получен', field='file')

    file_storage = request.app.get('file_storage')
    data = FileData(file_name=file.filename, file_body=file.file)
    data = await upload_file(data, file_storage)
    return json_response(data)
