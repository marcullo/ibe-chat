import enum


class RequestType(enum.Enum):
    SEND_MSG = 0


class Request:
    _types = {
        RequestType.SEND_MSG: 'send_msg'
    }

    def __init__(self, req_type, val):
        if req_type not in self._types:
            raise ValueError('Invalid request type!')
        self._type = req_type
        self._val = str(val)

    def __repr__(self):
        return '{}:{}'.format(self._types[self._type], self._val)

    @staticmethod
    def create(string):
        if string == '':
            raise ValueError('Invalid request string!')

        colon_id = string.index(':')
        req_type = None
        req_name = string[0:colon_id]
        for k, v in Request._types.items():
            if req_name == v:
                req_type = k
                break
        if req_type is None:
            raise ValueError('Invalid request type!')

        return Request(req_type, string[colon_id + 1:])

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._val

    @property
    def name(self):
        return self._types[self._type]
