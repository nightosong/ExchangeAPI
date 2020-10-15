# 文档说明

对官方接口进行了简单的封装，方便自己日常使用  

# Python Api

类结构:
```python
class BaseClient(object):
    def __init__(self, **kwargs):
        self._api_key = kwargs.get('api_key', None)
        self._secret_key = kwargs.get('secret_key', None)
        self._server_url = ''
        self._headers = {
            'Content-Type': 'application/json
        }

    def _unsigned_request(self, method, path, params=None):
        url = self._server_url + path
        rsp = requests.request(method, url, params=params)
        return rsp.json()

    def _signed_request(self, method, path, params=None):
        url = self._server_url + path
        # calculate signature
        sign = '???'

        rsp = requests.request(method, url, params=params)
        return rsp.json()

    def unsigned_api(self, param1, param2):
        path = ''
        params = {
            'param1': param1,  # statement
            'param2': param2,  # statement
        }
        return self._unsigned_request('GET', path, params)

    def signed_api(self, param1, param2):
        path = ''
        params = {
            'param1': param1,  # statement
            'param2': param2,  # statement
        }
        return self._signed_request('POST', path, params)

```

# WebSocket
