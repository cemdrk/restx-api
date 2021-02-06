
import datetime

from flask_restx import Resource, Namespace, fields
from flask import current_app, request
from flask_jwt_extended import create_access_token
from flask_api import status
from marshmallow import ValidationError

from ..models.user import UserModel
from ..schemas.auth import LoginSchema
from . import INTERNAL_ERROR_MSG


login_schema = LoginSchema()

ns = Namespace('auth', description='auth operations')

login_payload = ns.model('Login', {
    'username': fields.String,
    'password': fields.String
})


class Login(Resource):
    @ns.doc('user_login')
    @ns.doc(security=None)
    @ns.expect(login_payload, validate=False)
    def post(self):
        '''Authorize user'''

        try:
            validated_data = login_schema.load(request.get_json())
        except ValidationError as ve:
            resp_status = status.HTTP_400_BAD_REQUEST
            return dict(msg=ve.messages), resp_status
        except Exception:
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return dict(msg=INTERNAL_ERROR_MSG), resp_status

        user = UserModel.find_by_username(validated_data['username'])

        if user and user.check_password(validated_data['password']):
            expires = datetime.timedelta(
                minutes=current_app.config.get('TOKEN_EXPIRE_TIME', 20))

            access_token = create_access_token(
                identity=user.id, expires_delta=expires)

            return dict(access_token=access_token)

        return dict(msg='Invalid credentials'), status.HTTP_400_BAD_REQUEST


ns.add_resource(Login, '/login')
