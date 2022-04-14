from marshmallow import Schema, fields
from marshmallow.validate import ValidationError

import datetime


def released_validator(released: str):
    try:
        datetime.datetime.strptime(released, '%Y-%m-%d')
    except ValueError:
        raise ValidationError


class SongSchema(Schema):
    id = fields.String(required=True)
    artist = fields.String(required=True)
    title = fields.String(required=True)
    difficulty = fields.Float(required=True)
    level = fields.Integer(required=True)
    released = fields.String(required=True, validate=released_validator)
