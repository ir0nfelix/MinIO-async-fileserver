from envparse import env


DEBUG = env('DEBUG', default=False, cast=bool)

HOST = env('HOST', default='127.0.0.1')
PORT = env('PORT', default=5000, cast=int)

MAX_FILE_SIZE = env('MAX_FILE_SIZE',  1024 * 1024 * 5, cast=int)

SECRET_KEY = env('SECRET_KEY', default='sapsanshop')
AUTHENTICATION_BACKEND = 'authentication.JSONWebTokenAuthentication'

# region Minio
MINIO_SCHEME = env('MINIO_SCHEME', default='http')
MINIO_HOST = env('MINIO_HOST', default='127.0.0.1')
MINIO_PORT = env('MINIO_PORT', '9000')

MINIO_ACCESS_KEY = env('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = env('MINIO_SECRET_KEY', 'minioadmin')

MINIO_SECURE = env('MINIO_SECURE', False, cast=bool)

MINIO_BUCKET_NAME = env('MINIO_BUCKET_NAME', 'sapsanshop')

STORAGE_CLASS = env('STORAGE_CLASS', 'storage.MinioStorage')
# endregion

# region Redis
REDIS_SCHEME = env('REDIS_SCHEME', 'redis')
REDIS_HOST = env('REDIS_HOST', 'localhost')
REDIS_PORT = env('REDIS_PORT', '6379')

REDIS_DB = env('REDIS_DB', 5, cast=int)
REDIS_EXPIRE = env('REDIS_EXPIRE', 24 * 60 * 60, cast=int)
REDIS_MINPOOL = env('REDIS_MINPOOL', 1, cast=int)
REDIS_MAXPOOL = env('REDIS_MAXPOOL', 10, cast=int)
REDIS_KEY_PREFIX = 'fileserver'
# endregon

FILE_FIELD_NAME = env('FILE_FIELD_NAME', 'file')

