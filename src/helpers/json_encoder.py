
from bson.json_util import default
from json import JSONEncoder
from mongoengine import Document


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Document):
            return o.to_mongo()
        return default(o)
