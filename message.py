import json


class Message:
    def __init__(self, sender, recipient, message, timestamp=0):
        self._content = {
            'sender': str(sender),
            'recipient': str(recipient),
            'message': str(message),
            'timestamp': timestamp
        }

    def __repr__(self):
        return json.dumps(self._content)

    @staticmethod
    def create(string, timestamp=0):
        obj = json.loads(string)
        if timestamp is not 0:
            obj['timestamp'] = timestamp
        return Message(obj['sender'], obj['recipient'], obj['message'], obj['timestamp'])

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

    @property
    def timestamp(self):
        return self._content['timestamp']
