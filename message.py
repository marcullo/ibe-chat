import json


class Message:
    def __init__(self, sender, recipient, message):
        self._content = {
            'sender': str(sender),
            'recipient': str(recipient),
            'message': str(message)
        }

    def __repr__(self):
        return json.dumps(self._content)

    @staticmethod
    def create(string):
        obj = json.loads(string)
        return Message(obj['sender'], obj['recipient'], obj['message'])

    @property
    def content(self):
        return self._content

    @property
    def sender(self):
        return self._content['sender']

    @property
    def recipient(self):
        return self._content['recipient']

    @property
    def message(self):
        return self._content['message']
