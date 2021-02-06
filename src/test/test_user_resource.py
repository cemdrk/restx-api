
import unittest
import json

from base import BaseTestCase
from src.models.user import UserModel


def register_user(self):
    return self.client.post(
        '/users/',
        data=json.dumps(dict(
            email='user@mail.com',
            username='username',
            password='123456',
            first_name='firstname',
            last_name='lastname'
        )),
        content_type='application/json'
    )


class TestRegisterEndpoint(BaseTestCase):

    def setUp(self):
        UserModel.drop_collection()

    def test_register_status_code(self):
        with self.client:
            response = register_user(self)
            json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)

    def tearDown(self):
        UserModel.drop_collection()


if __name__ == '__main__':
    unittest.main()
