from abc import ABC
from dataclasses import dataclass
from marshmallow import Schema
from typing import List, Optional

from lib.types import TJSON


class AggregationEmptyException(Exception):
    """Exception for empty result aggregation"""


@dataclass
class FieldStatisticsResponse:
    average: float
    lowest: int
    highest: int

    def json(self):
        return {
            'average': self.average,
            'lowest': self.lowest,
            'highest': self.highest
        }


class BaseDatabaseController(ABC):
    def find(
            self,
            collection: str,
            search_schema: Schema,
            page_number: int = 1,
    ) -> List[TJSON]:
        raise NotImplementedError('Method search is not implemented.')

    def search_text(
            self,
            collection: str,
            search_schema: Schema,
            text: str,
    ) -> List[TJSON]:
        raise NotImplementedError('Method search_text is not implemented.')

    def get_average_of_field(
            self,
            collection: str,
            target_field: str,
            match: Optional[TJSON] = None,
    ) -> TJSON:
        raise NotImplementedError('Method get_average_of_field is not implemented.')

    def get_statistics_of_field(
            self,
            collection: str,
            target_field: str,
            match: Optional[TJSON] = None,
    ) -> FieldStatisticsResponse:
        raise NotImplementedError('Method get_statistics_of_field is not implemented.')

    def save(
            self,
            collection: str,
            schema: Schema,
            doc: TJSON,
    ):
        raise NotImplementedError('Method save is not implemented.')
