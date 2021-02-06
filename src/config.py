
import os


class Config:
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'secret')
    TOKEN_EXPIRE_TIME = 20  # minutes
    MONGODB_HOST = 'mongodb'
    CACHE_REDIS_HOST = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300  # seconds


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    MONGODB_DB = 'dev'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_DB = 'test'


config_by_name = dict(
    dev=DevelopmentConfig(),
    test=TestingConfig(),
)
