import importlib


def get_class_by_path(path):
    module_path, class_name = path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def format_bytes(bytes_num):
    sizes = ("B", "KB", "MB", "GB")

    i = 0
    byte = bytes_num

    while i < len(sizes) and bytes_num >= 1024:
        byte = bytes_num // 1024
        i = i + 1
        bytes_num = bytes_num // 1024

    return f'{byte} {sizes[i]}'
