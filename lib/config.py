from typing import Callable, Any

import os


def get_env(name: str, default: Any = None, cast: Callable[[Any], Any] = lambda x: x):
    value = os.getenv(name) or default
    return cast(value)


class BaseConfig:
    DB_HOST = get_env('DB_HOST', default='localhost')
    DB_PORT = get_env('DB_PORT', default='27017', cast=int)
    FLASK_PORT = get_env('FLASK_PORT', default='80', cast=int)
    SEARCH_SIZE = 5
    PATH_TO_DATA = get_env('PATH_TO_DATA', default='./migrations/songs.json')


class ProductionConfig(BaseConfig):
    pass


class TestConfig(BaseConfig):
    PATH_TO_DATA = './tests/songs.json'
