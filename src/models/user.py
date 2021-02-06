
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from ..db import db


class UserModel(db.Document):
    meta = {'collection': 'contacts'}

    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField(unique=True)
    username = db.StringField(unique=True)
    password = db.StringField()
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(self.__class__, self).save(*args, **kwargs)

    def save_to_db(self):
        self.save()

    def delete_from_db(self):
        self.delete()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_password(self, password):
        self.password = generate_password_hash(password)
        self.save_to_db()

    def update(self, updated_data):
        for key, val in updated_data.items():
            setattr(self, key, val)
        self.save_to_db()

    @classmethod
    def find_by_username(cls, username):
        return cls.objects.filter(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects.filter(id=_id).first()
