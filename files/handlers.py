import os
from uuid import uuid4

import magic
import png
from PIL import Image

from exceptions import FileServerError
from .dataclassess import FileData


class FileHandlerFactory(object):
    def create_file_handler(self, file: FileData):
        file_body = file.file_body
        file_body.seek(0, os.SEEK_END)
        length = file_body.tell()
        file_body.seek(0)
        type = magic.from_buffer(file_body.read(length), mime=True)
        file_body.seek(0)
        if type == 'image/jpeg' or type == 'image/pjpeg':
            return JpegHandler(file_body.raw, file.file_name, type, length)
        elif type == 'image/png':
            return PngHandler(file_body.raw, file.file_name, type, length)
        else:
            raise FileServerError('Неподдерживаемый формат файла', field='file')


class FileHandler(object):
    DEFAULT_EXT = ''

    def __init__(self, file_stream, filename, type_, length):
        self.file_stream = file_stream
        self.orig_file_name = filename
        self.file_type = type_
        self.file_length = length
        self.minio_file_name = None
        self.after_init()

    def after_init(self):
        pass

    def get_file_data(self):
        return {
            'minio_file_name': self._generate_filename(),
            'file_type': self.file_type,
            'orig_file_name': self.orig_file_name,
            'file_size': self.file_length,
            'extra_data': self.get_extra_data()
        }

    def get_extra_data(self):
        return {}

    def process_file(self):
        pass

    async def save(self, storage):
        await storage.save(self.minio_file_name, self.file_stream)

    def _generate_filename(self):
        if not self.minio_file_name:
            self.minio_file_name = '{}.{}'.format(uuid4().hex, self.DEFAULT_EXT)
        return self.minio_file_name


class JpegHandler(FileHandler):
    DEFAULT_EXT = 'jpeg'
    image = None

    def after_init(self):
        self.image = Image.open(self.file_stream)

    def process_file(self):
        if not self.image.info.get("progressive", False):
            self.make_progressive(self.image)
        else:
            self.file_stream.seek(0)

    def make_progressive(self, file):
        from io import BytesIO
        output = BytesIO()
        try:
            file.save(output, 'JPEG', progressive=True)
            self.file_stream.close()
            self.file_stream = output
            self.file_length = self.file_stream.seek(0, os.SEEK_END)
            self.file_stream.seek(0)
        except:
            output.close()

    def get_extra_data(self):
        return {
            'original_size': {
                'width': self.image.size[0],
                'height': self.image.size[1]
            }
        }


class PngHandler(FileHandler):
    DEFAULT_EXT = 'png'
    image = None

    def after_init(self):
        r = png.Reader(self.file_stream)
        self.image = r.read()

    def process_file(self):
        if not self.image[3].get("interlace", False):
            self.make_interlace(self.image)
        else:
            self.file_stream.seek(0)

    def make_interlace(self, file):
        from io import BytesIO
        output = BytesIO()
        try:
            info = file[3]
            info['interlace'] = True
            writer = png.Writer(**info)
            writer.write(output, file[2])
            self.file_stream.close()
            self.file_stream = output
            self.file_length = self.file_stream.seek(0, os.SEEK_END)
            self.file_stream.seek(0)
        except:
            output.close()

    def get_extra_data(self):
        return {
            'original_size': {
                'width': self.image[0],
                'height': self.image[1]
            }
        }
