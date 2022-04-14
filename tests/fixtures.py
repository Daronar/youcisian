from typing import List, Dict, Optional

from api.api import prepare_app
from lib.config import TestConfig
from migrations.migration import migrate

import json
import pytest
import time


@pytest.fixture(scope='class')
def config_for_test():
    yield TestConfig()


class SongsFromJson:
    songs: List[Dict]

    def __init__(self, path_to_json: str):
        self.songs = []
        with open(path_to_json) as f:
            for song in f.readlines():
                if not song:
                    continue
                self.songs.append(
                    json.loads(song)
                )

    def __len__(self):
        return len(self.songs)

    def __iter__(self):
        return iter(self.songs)

    def get_difficulties(self, level: Optional[int] = None) -> List[float]:
        if level is None:
            return [song['difficulty'] for song in self.songs]
        else:
            return [song['difficulty'] for song in self.songs if song['level'] == level]


@pytest.fixture(scope='class')
def songs_from_json(config_for_test) -> SongsFromJson:
    return SongsFromJson(path_to_json=config_for_test.PATH_TO_DATA)


@pytest.fixture(scope='class')
def mongo(docker_ip, docker_services, config_for_test):
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for('mongo', 27017)
    url = f'http://{docker_ip}:{port}'
    time.sleep(5)
    migrate(config_for_test)
    return url


@pytest.fixture()
def app(config_for_test):
    app = prepare_app(config_for_test)
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

