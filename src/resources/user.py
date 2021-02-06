
from flask_restx import Resource, Namespace, fields
from flask import current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_api import status
from mongoengine import errors as mongoengine_errors
from pymongo import errors as pymongo_errors
from werkzeug.security import generate_password_hash

import marshmallow

from ..models.user import UserModel
from ..schemas.user import UserSchema, ChangePasswordSchema, UserUpdateSchema
from ..cache import cache
from . import INTERNAL_ERROR_MSG

ns = Namespace('users', description='user operations')

NOT_FOUND_MSG = 'User not found'
EXISTS_MSG = 'User exists'

user_schema = UserSchema()
users_schema = UserSchema(many=True)
change_pass_schema = ChangePasswordSchema()
user_update_schema = UserUpdateSchema()


user_create_payload = ns.model('UserCreate', dict(
    first_name=fields.String,
    last_name=fields.String,
    email=fields.String,
    username=fields.String,
    password=fields.String)
)

user_update_payload = ns.model('UserUpdate', dict(
    first_name=fields.String,
    last_name=fields.String,
))

change_pass_payload = ns.model('ChangePassword', dict(
    old=fields.String,
    new=fields.String,
    confirm=fields.String,
))


class UserList(Resource):

    @ns.doc('list_users')
    @jwt_required
    def get(self):
        '''List all users'''

        return users_schema.dump(UserModel.objects.all())

    @ns.doc('create_user')
    @ns.doc(security=None)
    @ns.expect(user_create_payload, validate=False)
    def post(self):
        '''Create a user'''

        try:
            validated_data = user_schema.load(request.get_json())
        except marshmallow.ValidationError as ve:
            return dict(msg=ve.messages), status.HTTP_400_BAD_REQUEST
        except Exception as e:
            current_app.logger.error(e)
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return dict(msg=INTERNAL_ERROR_MSG), resp_status

        try:
            validated_data['password'] = generate_password_hash(
                validated_data['password'])
            user = UserModel(**validated_data)
            user.save_to_db()
        except pymongo_errors.DuplicateKeyError:
            return dict(msg=EXISTS_MSG), status.HTTP_400_BAD_REQUEST
        except mongoengine_errors.NotUniqueError:
            return dict(msg=EXISTS_MSG), status.HTTP_400_BAD_REQUEST
        except Exception as e:
            current_app.logger.error(e)
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return dict(msg=INTERNAL_ERROR_MSG), resp_status

        return user_schema.dump(user), status.HTTP_201_CREATED


@ns.response(status.HTTP_404_NOT_FOUND, 'User not found')
class User(Resource):

    @ns.doc('get_a_user')
    @jwt_required
    def get(self, user_id):
        '''Get a user'''

        cached = cache.get(user_id)
        if cached:
            return user_schema.dump(cached)

        try:
            user = UserModel.find_by_id(user_id)
        except mongoengine_errors.ValidationError:
            return dict(msg=NOT_FOUND_MSG), status.HTTP_404_NOT_FOUND
        except Exception as e:
            current_app.logger.error(e)
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return dict(msg=INTERNAL_ERROR_MSG), resp_status

        if not user:
            return dict(msg=NOT_FOUND_MSG), status.HTTP_404_NOT_FOUND

        cache.set(user_id, user)
        return user_schema.dump(user)

    @ns.doc('delete_a_user')
    @ns.response(status.HTTP_204_NO_CONTENT, 'User deleted')
    @jwt_required
    def delete(self, user_id):
        '''Delete a user'''

        user = UserModel.find_by_id(user_id)
        if not user:
            return dict(msg=NOT_FOUND_MSG), status.HTTP_404_NOT_FOUND

        cache.delete(user_id)

        user.delete_from_db()

        return '', status.HTTP_204_NO_CONTENT

    @ns.doc('update_a_user')
    @ns.expect(user_update_payload, validate=False)
    @jwt_required
    def put(self, user_id):
        '''Update a user'''

        try:
            validated_data = user_update_schema.load(request.get_json())
        except marshmallow.ValidationError as e:
            return e.msg, status.HTTP_400_BAD_REQUEST
        except Exception as e:
            current_app.logger.error(e)
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return dict(msg=INTERNAL_ERROR_MSG), resp_status

        user = UserModel.find_by_id(user_id)
        if not user:
            return dict(msg=NOT_FOUND_MSG), status.HTTP_404_NOT_FOUND

        user.update(validated_data)

        return user_schema.dump(user)


class ChangePassword(Resource):
    @ns.doc('change_user_pass')
    @ns.expect(change_pass_payload, validate=False)
    @jwt_required
    def post(self):
        '''Change user password'''

        try:
            validated_data = change_pass_schema.load(request.get_json())
        except marshmallow.ValidationError as e:
            return dict(msg=e.messages), status.HTTP_400_BAD_REQUEST
        except Exception as e:
            current_app.logger.error(e)
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return dict(msg=INTERNAL_ERROR_MSG), resp_status

        if validated_data['new'] != validated_data['confirm']:
            resp_status = status.HTTP_400_BAD_REQUEST
            return dict(msg='Confirmed password not match'), resp_status

        user_id = get_jwt_identity().get('$oid')

        user = UserModel.find_by_id(user_id)

        if not user.check_password(validated_data['old']):
            return dict(msg='Old pass not match'), status.HTTP_400_BAD_REQUEST

        user.update_password(validated_data['new'])

        return dict(msg='Password updated')


ns.add_resource(UserList, '/')
ns.add_resource(User, '/<user_id>')
ns.add_resource(ChangePassword, '/change-password')
