from flask import Flask, abort, Response
from flask_request_validator import (
    Param, GET, ValidRequest, Min, validate_params, JSON, CompositeRule,
    MinLength, MaxLength, Enum
)
from flask_request_validator.exceptions import InvalidRequestError

from lib.config import BaseConfig
from lib.db import AggregationEmptyException
from lib.db.mongo_db_controller import MongoDatabaseController
from lib.models.song import SongModel
from lib.models.song_rating import SongRatingModel
from lib.types import TJSON

import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def handle_exceptions(func):
    def wrapper(*args, **kwargs) -> TJSON:
        try:
            result = func(*args, **kwargs)
            return result
        except AggregationEmptyException as ae:
            logger.error(f'Exception {ae} occured while aggregation, check id is existed.')
            abort(Response('Empty aggregation', 404))
        except InvalidRequestError as re:
            logger.error(f'Exception {re} occured while {func.__name__}.')
            abort(Response('Invalid parameters of request', 400))
        except Exception as e:
            logger.error(f'Exception {e} occured while {func.__name__}.')
            abort(Response(f'Error occured while {func.__name__}.', 500))

    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/api/get-songs', methods=['GET'])
@handle_exceptions
@validate_params(
    Param('page', GET, int, rules=[Min(1)], required=False),
)
def get_songs(valid: ValidRequest) -> TJSON:
    """
    - A
      - Returns a list of songs with the data provided by the "songs.json".
      - Add a way to paginate songs.
    """
    params = valid.get_params()
    page_number = int(params.get('page', 1))
    return {
        'songs': SongModel.get_songs(
            controller=app.config['db'],
            page_number=page_number or 1,
        )
    }


@app.route('/api/search-songs', methods=['GET'])
@handle_exceptions
@validate_params(
    Param('message', GET, str, required=True),
)
def search_songs(valid: ValidRequest) -> TJSON:
    """
    - B
      - Returns the average difficulty for all songs.
      - Takes an optional parameter "level" to filter for only songs from a specific level.
    """
    search_query = valid.get_params().get('message')
    songs = SongModel.search_text(
        controller=app.config['db'],
        search_query=search_query,
    )
    seach_result_size = app.config['cfg'].SEARCH_SIZE
    return {
        'songs': songs[:seach_result_size]
    }


@app.route('/api/get-average-difficulties', methods=['GET'])
@handle_exceptions
@validate_params(
    Param('level', GET, int, rules=[Min(0)], required=False),
)
def get_average_difficulties(valid: ValidRequest) -> TJSON:
    """
    - C
      - Returns a list of songs matching the search string.
      - Takes a required parameter "message" containing the user's search string.
      - The search should take into account song's artist and title.
      - The search should be case insensitive.
    """
    level = valid.get_params().get('level')
    return SongModel.get_average_difficulty(
        controller=app.config['db'],
        level=int(level) if level else None,
    )


@app.route('/api/add-rating-for-song', methods=['PUT'])
@handle_exceptions
@validate_params(
    Param('song_id', JSON, str, rules=CompositeRule(MinLength(32), MaxLength(32)), required=True),
    Param('rating', JSON, int, rules=[Enum(1, 2, 3, 4, 5)], required=True),
)
def add_rating_for_song(valid: ValidRequest) -> Response:
    """
    - D
      - Adds a rating for the given song.
      - Takes required parameters "song_id" and "rating"
      - Ratings should be between 1 and 5 inclusive.
    """
    data = valid.get_json()
    rating = int(data.get('rating'))
    song_id = data.get('song_id')

    SongRatingModel.add_rating_for_song(
        controller=app.config['db'],
        song_id=song_id,
        rating=rating,
    )
    return Response('', status=200)


@app.route('/api/get-rating-statistics-for-song', methods=['GET'])
@handle_exceptions
@validate_params(
    Param('song_id', GET, str, rules=CompositeRule(MinLength(32), MaxLength(32)), required=True),
)
def get_rating_statistics_for_song(valid: ValidRequest) -> TJSON:
    """
    - E
      - Returns the average, the lowest and the highest rating of the given song id.
    """
    song_id = valid.get_params().get('song_id')
    return SongRatingModel.get_song_rating_statistics(
        controller=app.config['db'],
        song_id=song_id,
    ).json()


def prepare_app(config: BaseConfig):
    db_controller = MongoDatabaseController(
        host=config.DB_HOST,
        port=config.DB_PORT,
        db='songs'
    )

    app.config['db'] = db_controller
    app.config['cfg'] = config
    return app
