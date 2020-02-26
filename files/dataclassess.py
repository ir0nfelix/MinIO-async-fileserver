from dataclasses import dataclass
from io import BufferedReader


@dataclass
class FileData:
    file_name: str
    file_body: BufferedReader
