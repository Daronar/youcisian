from marshmallow import Schema, fields
from marshmallow.validate import Range


class SongRatingSchema(Schema):
    id = fields.String(required=True)
    rating = fields.Int(strict=True, validate=[Range(min=1, max=5, error="Value must be greater than 0 and less than 6")])
