import re


class Identity:
    def __init__(self, name, email):
        self._name = name
        self._email = email

    def __repr__(self):
        return '{}<{}>'.format(self._name, self._email)

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @staticmethod
    def create(string):
        res = re.split('<', string)
        return Identity(res[0], res[1])
