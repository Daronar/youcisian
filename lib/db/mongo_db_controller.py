import uuid

from marshmallow import Schema, ValidationError
from pymongo import MongoClient
from pymongo.database import Database
from typing import List, Optional

import logging

from lib.db import BaseDatabaseController, FieldStatisticsResponse, AggregationEmptyException
from lib.types import TJSON

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


PAGE_SIZE = 5


class MongoDatabaseController(BaseDatabaseController):
    _client: MongoClient
    _db: Database

    def __init__(
            self,
            host: str,
            port: int,
            db: str,
    ):
        super().__init__()
        self._client = MongoClient(host=host, port=port)
        self._db = self._client[db]

    @staticmethod
    def validate_docs_by_schema(
            schema: Schema,
            docs: List[TJSON]
    ) -> List[TJSON]:
        validated_docs = []
        for doc in docs:
            try:
                validated_docs.append(
                    schema.load(doc)
                )
            except ValidationError:
                logger.error(f'Document {doc} from database doesn\'t correspond to required schema.')

        return validated_docs

    def find(
            self,
            collection: str,
            search_schema: Schema,
            page_number: int = 1,
    ) -> List[TJSON]:
        page_number -= 1
        collection = self._db[collection]
        projection = {field_name: 1 for field_name in search_schema.fields}
        projection.update({'_id': 0})
        docs = collection.find(
            filter={},
            projection=projection,
        ).sort('_id').skip(page_number * PAGE_SIZE).limit(PAGE_SIZE)
        return self.validate_docs_by_schema(schema=search_schema, docs=docs)

    def search_text(
            self,
            collection: str,
            search_schema: Schema,
            text: str,
    ) -> List[TJSON]:
        collection = self._db[collection]
        projection = {field_name: 1 for field_name in search_schema.fields}
        projection.update({'_id': 0})
        docs = collection.find(
            filter={
                '$text': {'$search': text}
            },
            projection=projection,
        )
        return self.validate_docs_by_schema(schema=search_schema, docs=docs)

    def _get_aggr_functions_of_field(
            self,
            collection: str,
            target_field: str,
            aggr_functions: List[str],
            match: Optional[TJSON] = None,
    ) -> TJSON:
        collection = self._db[collection]
        group = {
            f'{aggr_function}_value': {
                f'${aggr_function}': f'${target_field}'
            }
            for aggr_function in aggr_functions
        }
        group.update({'_id': 1})

        project = {
            f'{aggr_function}_value': 1
            for aggr_function in aggr_functions
        }
        project.update({'_id': 0})
        aggr_value = collection.aggregate(
            [
                {
                    '$match': match or {}
                },
                {
                    '$group': group
                },
                {
                    '$project': project
                }
            ]
        )
        aggr_value = list(aggr_value)
        if not aggr_value:
            raise AggregationEmptyException(
                f'Aggregation functions has returned empty result '
                f'for collection {collection}, field {target_field} and match {match}.'
            )
        return aggr_value[0]

    def get_average_of_field(
            self,
            collection: str,
            target_field: str,
            match: Optional[TJSON] = None,
    ) -> TJSON:
        average = self._get_aggr_functions_of_field(
            collection=collection,
            target_field=target_field,
            match=match,
            aggr_functions=['avg']
        )
        return average

    def get_statistics_of_field(
            self,
            collection: str,
            target_field: str,
            match: Optional[TJSON] = None,
    ) -> FieldStatisticsResponse:
        statistics = self._get_aggr_functions_of_field(
            collection=collection,
            target_field=target_field,
            match=match,
            aggr_functions=['avg', 'max', 'min']
        )
        return FieldStatisticsResponse(
            average=statistics['avg_value'],
            lowest=statistics['min_value'],
            highest=statistics['max_value']
        )

    def save(
            self,
            collection: str,
            schema: Schema,
            doc: TJSON,
    ):
        collection = self._db[collection]
        if not doc.get('id'):
            doc['id'] = uuid.uuid4().hex

        try:
            collection.insert_one(
                document=schema.dump(doc)
            )
        except ValidationError:
            logger.error(f'Document {doc} from database doesn\'t correspond to required schema.')
