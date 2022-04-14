import pytest
import random

from fixtures import mongo, app, client, config_for_test


@pytest.mark.usefixtures('mongo')
class TestSongsRatings:
    @pytest.mark.parametrize('invalid_data', [{},
                                              {'a': 1},
                                              {'song_id': '927ab09db98642bd8ea89847800dc'},
                                              {'song_id': '927ab09db98642bd8ea89847800dc724'},
                                              {'rating': 0},
                                              {'ratings': 4},
                                              {'rating': 5},
                                              {
                                                  'song_id': '927ab09db98642bd8ea89847800dc724',
                                                  'rating': 6,
                                              },
                                              {
                                                  'song_id': '927ab09db98642bd8ea89847800dc7',
                                                  'rating': 4,
                                              }])
    def test_put_songs_ratings_invalid_params(self, client, invalid_data):
        response = client.put(f'api/add-rating-for-song', json=invalid_data)
        assert response.status_code == 400

    @pytest.mark.parametrize('invalid_param', [None, 'song_id=', 'song_id=asd', 'bs=1'])
    def test_get_rating_statistics_for_song_invalid_params(self, client, invalid_param):
        path = f'api/get-rating-statistics-for-song?{invalid_param}' if invalid_param is not None else 'api/get-rating-statistics-for-song'
        response = client.get(path)
        assert response.status_code == 400

    def test_get_rating_statistics_for_song_for_not_existed_song(self, client):
        invalid_song_id = '1' * 32
        response = client.get(f'api/get-rating-statistics-for-song?song_id={invalid_song_id}')
        assert response.status_code == 404

    def test_put_rating_for_song(self, client):
        doc = {
            'song_id': '2' * 32,
            'rating': 3
        }
        response = client.put('api/add-rating-for-song', json=doc)

        assert response.status_code == 200

    def test_put_rating_and_get_rating_statistic(self, client):
        song_id = '3' * 32
        ratings = []
        for _ in range(10):
            ratings.append(random.randint(1, 5))
            doc = {
                'song_id': song_id,
                'rating': ratings[-1]
            }
            client.put('api/add-rating-for-song', json=doc)

        assert client.get()

        response = client.get(f'api/get-rating-statistics-for-song?song_id={song_id}')
        assert response == 200
        response_data = response.json
        assert type(response_data) == dict
        assert response_data == {
          "average": sum(ratings) /len(ratings),
          "highest": max(ratings),
          "lowest": min(ratings)
        }
