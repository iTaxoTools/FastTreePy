#-----------------------------------------------------------------------------
# Copyright notice goes here
#-----------------------------------------------------------------------------

import importlib.resources
import numpy
import json

_resource_path = importlib.resources.files(__package__)
def get_resource(path):
    return str(_resource_path / path)

def zeros(slots):
    return numpy.zeros(slots)

def config():
    with open(get_resource('config.json')) as config:
        data = config.read()
    return json.loads(data)
