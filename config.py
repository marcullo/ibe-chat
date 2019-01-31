import json


def load():
    with open('config.json') as f:
        return json.load(f)
