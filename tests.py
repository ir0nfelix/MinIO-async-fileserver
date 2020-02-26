import jwt
import json
from io import BytesIO

from aiohttp import web, FormData
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from unittest.mock import patch, MagicMock, Mock

from asyncio import coroutine

import settings
from files.routes import routes
from middleware import error_middleware
from storage import TestStorage
from utils import format_bytes


def mocked_method(*args, **kwargs):
    pass


class Image:
    info = {}

    def __init__(self, info):
        self.info = info

    def save(self, *args, **kwargs):
        pass


class ImageWithError(Image):
    def save(self):
        raise Exception()


class PngReader(object):
    def __init__(self, *args, **kwargs):
        pass

    def read(self, **kwargs):
        return (
            '500',
            '500',
            MagicMock(),
            {
                'interlace': False
            }
        )


class PngWriter(PngReader):
    def write(self, *args, **kwargs):
        raise Exception()


def CoroMock():
    coro = Mock(name="CoroutineResult")
    corofunc = Mock(name="CoroutineFunction", side_effect=coroutine(coro))
    corofunc.coro = coro
    return corofunc


class BaseTestsViews(AioHTTPTestCase):

    async def get_application(self):
        app = web.Application(
            middlewares=[error_middleware],
            client_max_size=settings.MAX_FILE_SIZE
        )
        app['file_storage'] = app['redis_storage'] = TestStorage()
        for route in routes:
            app.router.add_route(**route)
        return app

    async def create_upload_request(self, data=None, headers=None, token=None):
        if not headers:
            if not token:
                token = self.jwt_encode().decode()
            headers = {'Authorization': 'Bearer ' + token}
        resp = await self.client.request('POST', '/upload/', data=data, headers=headers)
        return resp

    def validate_return_object(self, data):
        self.assertIn('id', data)
        self.assertIn('file_size', data)
        self.assertIn('file_name', data)
        self.assertIn('orig_file_name', data)
        self.assertIn('file_type', data)

    async def upload_and_test(self, file_type):
        data = FormData()
        data.add_field('file',
                       BytesIO(b'my file contents'),
                       filename='hello_world.jpg',
                       content_type=file_type)
        response = await self.create_upload_request(data)
        response_data = await response.content.readline()
        self.assertEqual(response.status, 200)
        data = json.loads(response_data)
        self.validate_return_object(data)
        self.assertEqual(data['file_type'], file_type)

    def jwt_encode(self, headers=None):
        return jwt.encode({'test': 'data'}, settings.SECRET_KEY, headers=headers)


@patch('files.handlers.png')
@patch('files.handlers.magic.from_buffer')
@patch('files.handlers.PngHandler.get_extra_data')
class PngTestViews(BaseTestsViews):
    @unittest_run_loop
    async def test_upload_png_when_not_interlace(self, get_extra_data_mock, magic_mock, png_mock):
        get_extra_data_mock.return_value = {}
        magic_mock.return_value = 'image/png'
        file_type = 'image/png'
        await self.upload_and_test(file_type)

    @unittest_run_loop
    async def test_upload_png_when_interlace(self, get_extra_data_mock, magic_mock, png_mock):
        get_extra_data_mock.return_value = {}
        magic_mock.return_value = 'image/png'
        png_mock.Reader = PngReader
        file_type = 'image/png'
        await self.upload_and_test(file_type)

    @unittest_run_loop
    async def test_upload_png_when_make_interlace_raises_error(self, get_extra_data_mock, magic_mock, png_mock):
        get_extra_data_mock.return_value = {}
        magic_mock.return_value = 'image/png'
        png_mock.Reader = PngReader
        png_mock.Writer = PngWriter
        file_type = 'image/png'
        await self.upload_and_test(file_type)


@patch('files.handlers.Image')
@patch('files.handlers.magic.from_buffer')
@patch('files.handlers.JpegHandler.get_extra_data')
class JpgTestViews(BaseTestsViews):
    @unittest_run_loop
    async def test_upload_jpg(self, get_extra_data_mock, magic_mock, image_mock):
        get_extra_data_mock.return_value = {}
        image_mock.open.return_value = Image({'is_progressive': 1})
        magic_mock.return_value = 'image/jpeg'
        file_type = 'image/jpeg'
        await self.upload_and_test(file_type)

    @unittest_run_loop
    async def test_upload_non_progressive_jpg(self, get_extra_data_mock, magic_mock, image_mock):
        get_extra_data_mock.return_value = {}
        magic_mock.return_value = 'image/jpeg'
        image_mock.open.return_value = Image({'progressive': True})
        file_type = 'image/jpeg'
        await self.upload_and_test(file_type)

    @unittest_run_loop
    async def test_upload_non_progressive_jpg_when_save_raises_error(self, get_extra_data_mock, magic_mock, image_mock):
        get_extra_data_mock.return_value = {}
        magic_mock.return_value = 'image/jpeg'
        image_mock.open = MagicMock(return_value=ImageWithError({}))
        file_type = 'image/jpeg'
        await self.upload_and_test(file_type)


@patch('files.handlers.magic.from_buffer')
class PdfTestViews(BaseTestsViews):
    @unittest_run_loop
    async def test_upload_pdf(self, magic_mock):
        magic_mock.return_value = 'application/pdf'
        file_type = 'application/pdf'
        await self.upload_and_test(file_type)


class AppTestViews(BaseTestsViews):

    @unittest_run_loop
    async def test_index(self):
        response = await self.client.request('GET', '/')
        response_data = await response.content.readline()
        self.assertEqual(response.status, 200)
        self.assertEqual(response_data.decode('ASCII'), 'File Server')

    @unittest_run_loop
    @patch('files.handlers.magic.from_buffer')
    async def test_upload_unnknown_type_should_return_400(self, magic_mock):
        magic_mock.return_value = 'unknown/format'
        data = FormData()
        data.add_field('file',
                       BytesIO(b'my file contents'),
                       filename='hello_world.jpg',
                       content_type='unknown/format')
        response = await self.create_upload_request(data)
        self.assertEqual(response.status, 400)

    @unittest_run_loop
    @patch('files.handlers.magic.from_buffer')
    async def test_upload_oversize_file(self, magic_mock):
        magic_mock.return_value = 'image/jpeg'
        data = FormData()
        data.add_field('file',
                       BytesIO(b'*'*(settings.MAX_FILE_SIZE*2)),
                       filename='hello_world.jpg',
                       content_type='image/jpeg')
        response = await self.create_upload_request(data)
        self.assertEqual(response.status, 400)
        response_data = await response.content.readline()
        self.assertEqual(json.loads(response_data)['fields']['file'],
                         [f'Размер файла не должен превышать {format_bytes(settings.MAX_FILE_SIZE)}'])

    @unittest_run_loop
    async def test_bad_request(self):
        response = await self.create_upload_request()
        self.assertEqual(response.status, 400)
        response_data = await response.content.readline()
        self.assertEqual(json.loads(response_data)['fields']['file'], ['Файл не был получен'])

    @unittest_run_loop
    async def test_authentication(self):
        response = await self.create_upload_request(headers={'Authorization': 'Bearer '})
        response_data = await response.content.readline()
        self.assertEqual(response.status, 401)
        self.assertEqual(response_data.decode('ASCII'),
                         '"Invalid Authorization header. No credentials provided."')

        response = await self.create_upload_request(
            headers={'Authorization': 'Bearer extra ' + self.jwt_encode().decode()})
        response_data = await response.content.readline()
        self.assertEqual(response.status, 401)
        self.assertEqual(response_data.decode('ASCII'),
                         '"Invalid Authorization header. Credentials string should not contain spaces."')

        response = await self.create_upload_request(
            headers={'Authorization': 'OtherPrefix ' + self.jwt_encode().decode()})
        self.assertEqual(response.status, 401)

        response = await self.create_upload_request(headers={'Authorization': 'Bearer wrong_signature'})
        response_data = await response.content.readline()
        self.assertEqual(response.status, 401)
        self.assertEqual(response_data.decode('ASCII'),
                         '"Error decoding signature."')

        expired_token = jwt.encode({
            'test': 'data',
            'exp': 0
        }, settings.SECRET_KEY)
        response = await self.create_upload_request(
            headers={'Authorization': 'Bearer ' + expired_token.decode()})
        response_data = await response.content.readline()
        self.assertEqual(response.status, 401)
        self.assertEqual(response_data.decode('ASCII'),
                         '"Signature has expired."')

    @unittest_run_loop
    async def test_wrong_auth_backend(self):
        backend = settings.AUTHENTICATION_BACKEND
        try:
            settings.AUTHENTICATION_BACKEND = None
            response = await self.create_upload_request()
            self.assertEqual(response.status, 401)
        finally:
            settings.AUTHENTICATION_BACKEND = backend
