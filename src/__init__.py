
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager

from .config import config_by_name
from .db import db
from .cache import cache
from .helpers.json_encoder import MongoJSONEncoder
from .resources.auth import ns as auth_ns
from .resources.user import ns as user_ns


def create_app(config_name):
    app = Flask(__name__)
    app.json_encoder = MongoJSONEncoder
    app.config.from_object(config_by_name.get(config_name))

    authorizations = {'api_key': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
        }
    }

    api_opts = dict(
        version='1.0',
        title='RESTX API',
        authorizations=authorizations,
        description='RESTX API',
        security='api_key',
    )

    api = Api(app, **api_opts)

    api.add_namespace(auth_ns)
    api.add_namespace(user_ns)

    db.init_app(app)

    cache.init_app(app)

    JWTManager(app)

    return app
