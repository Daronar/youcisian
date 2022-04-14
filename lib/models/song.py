from typing import List, Optional

from lib.db import BaseDatabaseController
from lib.schemas.song import SongSchema
from lib.types import TJSON


class SongModel:
    collection = 'songs'
    schema = SongSchema()

    @classmethod
    def get_songs(
            cls,
            controller: BaseDatabaseController,
            page_number: int = 1
    ) -> List[TJSON]:
        return controller.find(
            collection=cls.collection,
            search_schema=cls.schema,
            page_number=page_number,
        )

    @classmethod
    def get_average_difficulty(
            cls,
            controller: BaseDatabaseController,
            level: Optional[int] = None,
    ) -> TJSON:
        return controller.get_average_of_field(
            collection=cls.collection,
            target_field='difficulty',
            match={
                'level': level
            } if level else None
        )

    @classmethod
    def search_text(
            cls,
            controller: BaseDatabaseController,
            search_query: str,
    ) -> List[TJSON]:
        return controller.search_text(
            collection=cls.collection,
            search_schema=cls.schema,
            text=search_query,
        )
