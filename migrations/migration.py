from lib.config import BaseConfig, ProductionConfig
from pymongo import MongoClient

import json
import uuid


def migrate(config: BaseConfig):
    client = MongoClient(host=config.DB_HOST, port=config.DB_PORT)
    client.drop_database(name_or_database='songs')

    print('Create database song.')
    db = client['songs']

    print('Create collection songs.')
    songs = db['songs']
    print('Create collection songs_ratings.')
    songs_ratings = db['songs_ratings']

    print('Migrate data to songs.')
    with open(config.PATH_TO_DATA) as data:
        for line in data.readlines():
            doc = json.loads(line)
            if not doc.get('id'):
                doc['id'] = uuid.uuid4().hex
            songs.insert_one(document=doc)

    print('Create indexes.')
    songs.create_index(keys='id')
    songs.create_index(keys=[('difficult', 1), ('level', 1)])
    songs.create_index(keys=[('artist', 'text'), ('title', 'text')])

    songs_ratings.create_index(keys='id')


if __name__ == '__main__':
    config = ProductionConfig()
    migrate(config)
