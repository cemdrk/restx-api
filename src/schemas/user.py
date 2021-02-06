
from marshmallow import Schema, fields, validates_schema, ValidationError, validate


def min_one_length(data):
    return validate.Length(min=1)(data)


def password_validator(data):
    return validate.Length(min=6, max=20)(data)


class UserSchema(Schema):
    class Meta:
        load_only = ('password',)
        dump_only = ('id',)

    id = fields.String()
    first_name = fields.Str(required=True, validate=[min_one_length, ])
    last_name = fields.Str(required=True, validate=[min_one_length, ])
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=[min_one_length, ])
    password = fields.Str(required=True, validate=[password_validator, ])
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class UserUpdateSchema(Schema):
    first_name = fields.Str(validate=[min_one_length, ])
    last_name = fields.Str(validate=[min_one_length, ])

    @validates_schema
    def at_least_one_field_exists(self, data, **kwargs):
        if not len(data):
            raise ValidationError('at least one field required')


class ChangePasswordSchema(Schema):
    class Meta:
        load_only = ('old', 'new', 'confirm')

    old = fields.Str(required=True,)
    new = fields.Str(required=True, validate=[password_validator, ])
    confirm = fields.Str(required=True, validate=[password_validator, ])
