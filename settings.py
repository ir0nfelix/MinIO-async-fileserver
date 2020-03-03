from envparse import env


DEBUG = env('DEBUG', default=False, cast=bool)

HOST = env('HOST', default='127.0.0.1')
PORT = env('PORT', default=5000, cast=int)

MAX_FILE_SIZE = env('MAX_FILE_SIZE',  1024 * 1024 * 5, cast=int)

BISTRO_IMAGE_SIZE = (env('BISTRO_IMAGE_WIDTH', 110, cast=int), env('BISTRO_IMAGE_HEIGHT', 110, cast=int))

# TODO JWT access
# SECRET_KEY = env('SECRET_KEY', default='sapsanshop')
# AUTHENTICATION_BACKEND = 'authentication.JSONWebTokenAuthentication'

FILE_FIELD_NAME = env('FILE_FIELD_NAME', 'file')

# region Minio
MINIO_SCHEME = env('MINIO_SCHEME', default='http')
MINIO_HOST = env('MINIO_HOST', default='127.0.0.1')
MINIO_PORT = env('MINIO_PORT', '9000')

MINIO_ACCESS_KEY = env('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = env('MINIO_SECRET_KEY', 'minioadmin')

MINIO_BUCKET_NAME = env('MINIO_BUCKET_NAME', 'sapsanshop')

STORAGE_CLASS = env('STORAGE_CLASS', 'storage.MinioStorage')
# endregion
