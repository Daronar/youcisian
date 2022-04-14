from lib.db import BaseDatabaseController, FieldStatisticsResponse
from lib.schemas.song_rating import SongRatingSchema


class SongRatingModel:
    collection = 'songs_ratings'
    schema = SongRatingSchema()

    @classmethod
    def add_rating_for_song(
            cls,
            controller: BaseDatabaseController,
            song_id: str,
            rating: int,
    ) -> None:
        controller.save(
            collection=cls.collection,
            schema=cls.schema,
            doc={
                'id': song_id,
                'rating': rating,
            }
        )

    @classmethod
    def get_song_rating_statistics(
            cls,
            controller: BaseDatabaseController,
            song_id: str,
    ) -> FieldStatisticsResponse:
        return controller.get_statistics_of_field(
            collection=cls.collection,
            target_field='rating',
            match={
                'id': song_id
            }
        )
