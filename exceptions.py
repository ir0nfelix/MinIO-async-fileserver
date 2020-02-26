import settings
from utils import format_bytes


class FileServerError(Exception):
    def __init__(self, message=None, status_code=400, field=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.field = field

    def to_dict(self):
        data = {
            "internalMessage": "Invalid input.",
            "userMessage": self.message,
            "errorCode": "invalid",
        }
        if self.field:
            data['userMessage'] = "Invalid input."
            data['fields'] = {self.field: [self.message]}
        return data


class OversizeFileError(FileServerError):
    def __init__(self):
        message = f'Размер файла не должен превышать {format_bytes(settings.MAX_FILE_SIZE)}'
        super().__init__(message=message, field='file')
