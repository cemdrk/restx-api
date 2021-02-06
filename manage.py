
import unittest
import os

from flask_script import Manager

from src import create_app


app = create_app(os.getenv('API_ENV', 'dev'))

manager = Manager(app)


@manager.command
def run():
    app.run(host=app.config.get('HOST'))


@manager.command
def test():
    tests = unittest.TestLoader().discover('src/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
