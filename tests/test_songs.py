import pytest

from fixtures import mongo, app, client, config_for_test, songs_from_json


@pytest.mark.usefixtures('mongo')
class TestSongs:
    PAGE_SIZE = 5

    @pytest.mark.parametrize('page', [None, 1, 2, 3, 100])
    def test_get_songs(self, client, page, songs_from_json):
        response = client.get(f'api/get-songs?page={page}' if page else 'api/get-songs')

        assert response.status_code == 200
        response_data = response.json
        assert 'songs' in response_data
        response_data = response_data['songs']
        assert type(response_data) == list
        if not page:
            assert len(response_data) == self.PAGE_SIZE
        elif page < 3:
            assert len(response_data) == self.PAGE_SIZE
        elif page == 3:
            assert len(response_data) == len(songs_from_json) - (page - 1) * self.PAGE_SIZE
        else:
            assert len(response_data) == 0

    @pytest.mark.parametrize('invalid_param', ['page=-1', 'page=0', 'page=adas'])
    def test_get_songs_invalid_params(self, client, invalid_param):
        response = client.get(f'api/get-songs?{invalid_param}')
        assert response.status_code == 400

    @pytest.mark.parametrize('message', ['youSiciaNs', 'youSiciaNs viValDi', 'youSiciaNs viValDi'])
    def test_search_songs(self, client, message, songs_from_json):
        def check_target_searching_doc_in_json():
            for doc in songs_from_json:
                if 'yousicians' in doc['artist'].lower() and 'vivaldi' in doc['title'].lower():
                    return
            assert False, 'No document for test_search_songs in source json data!'

        check_target_searching_doc_in_json()

        response = client.get(f'api/search-songs?message={message}')
        assert response.status_code == 200
        response_data = response.json
        assert 'songs' in response_data
        response_data = response_data['songs']
        assert type(response_data) == list

        splitted_query = message.split()
        if len(splitted_query) == 1:
            assert splitted_query[0].lower() in response_data[0]['artist'].lower()
        else:
            assert (splitted_query[0].lower() in response_data[0]['artist'].lower() or splitted_query[0].lower() in response_data[0]['title'].lower())
            assert (splitted_query[1].lower() in response_data[0]['artist'].lower() or splitted_query[1].lower() in response_data[0]['title'].lower())

    @pytest.mark.parametrize('message', ['', 'you'])
    def test_search_songs_empty_result(self, client, message):
        response = client.get(f'api/search-songs?message={message}')
        assert response.status_code == 200
        response_data = response.json
        assert 'songs' in response_data
        response_data = response_data['songs']
        assert type(response_data) == list
        assert len(response_data) == 0

    def test_search_songs_invalid_params(self, client):
        response = client.get(f'api/search-songs?bs=1')
        assert response.status_code == 400

    @pytest.mark.parametrize('level', [None, 6, 13])
    def test_get_average_difficulties(self, client, level, songs_from_json):
        path = f'api/get-average-difficulties?level={level}' if level is not None else 'api/get-average-difficulties'
        response = client.get(path)

        assert response.status_code == 200
        response_data = response.json
        assert type(response_data) == dict
        assert 'avg_value' in response_data

        js_songs_difficulties = songs_from_json.get_difficulties(level=level)
        assert response_data['avg_value'] == sum(js_songs_difficulties) / len(js_songs_difficulties)

    @pytest.mark.parametrize('level', [100, 1000])
    def test_get_average_difficulties_for_not_existed_level(self, client, level, songs_from_json):
        response = client.get(f'api/get-average-difficulties?level={level}')
        assert response.status_code == 404

    @pytest.mark.parametrize('invalid_param', ['level=-1', 'level=asda'])
    def test_get_average_difficulties_for_invalid_parameters(self, client, invalid_param):
        response = client.get(f'api/get-average-difficulties?{invalid_param}')
        assert response.status_code == 400
