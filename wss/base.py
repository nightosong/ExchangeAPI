import ast
import base64
import hashlib
import hmac
import json
import requests
import threading
import time
import websocket
import zlib
import ssl
import traceback

from urllib import parse
from datetime import datetime


def json_replace(msg):
    msg = msg.replace('true', 'True').replace('false', 'False').replace('null', 'None')
    return msg


class BaseClient(object):
    def __init__(self, **kwargs):
        self._api_key = kwargs.get('api_key')
        self._secret_key = kwargs.get('secret_key')
        self._socket = None
        self._thread = None
        self._state = False
        self._request = []

    @property
    def state(self):
        return self._state

    def start(self):
        raise NotImplementedError

    def on_open(self):
        raise NotImplementedError

    def on_close(self):
        self._state = False

    def on_error(self, errs):
        print(errs)

    def on_message(self, msg):
        raise NotImplementedError