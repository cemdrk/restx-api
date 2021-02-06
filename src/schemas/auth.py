
from marshmallow import Schema, fields


class LoginSchema(Schema):
    class Meta:
        load_only = ('password',)

    username = fields.Str(required=True)
    password = fields.Str(required=True)
