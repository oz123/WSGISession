import string
import uuid


VALID_KEY_CHARS = string.ascii_lowercase + string.digits


class SessionId:

    def __get__(self, obj, objtype):
        print('Retrieving')
        return self.key

    #def __set__(self, obj, val):
    #    print('Updating')
    #    self.key = key

    def __set__(self, s_obj, s_key):
        if not set(s_key).issubset(set(VALID_KEY_CHARS)):
            raise ValueError("Invalid characters in session key")
        setattr(s_obj, "id", s_key)
        self.key = s_key


class SimpleSession(object):

    def __init__(self):
        self.id = SessionId()
        self.data = {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def load(self, id):
        if id in self.manager:
            self.data = self.manager[id]
            self.id = id
        else:
            self.data = {}
            self.id = uuid.uuid4().hex

    def save(self):
        self.manager[self.id] = self.data
        return self.id


s = SimpleSession()

s.id = "asfasdfs?"
