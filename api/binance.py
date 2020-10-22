import hmac
import json
import time
import base64
import random
import hashlib
import requests

from urllib import parse
from operator import itemgetter
from datetime import datetime, timedelta


class BinanceClient(object):
    def __init__(self, **kwargs):
        self._api_key = kwargs.get("api_key", None)
        self._secret_key = kwargs.get("secret_key", None)
        self._server_url = 'https://api.binance.com'
        self._headers = {
            'X-MBX-APIKEY': self._api_key,
            'Content-Type': 'application/json'
        }
    def _unsigned_request(self, method, path, params=None):
        """无签名访问"""
        url = path if path.startswith('https') else self._server_url + path
        rsp = requests.request(method, url, params=params)
        return rsp.json()

    def _signed_request(self, method, path, params={}):
        """带签名访问"""
        url = self._server_url + path
        sign_params = {
            'timestamp': int(time.time() * 1000)
        }
        params = {f'{x}': params[x] for x in params if params[x]}  # 去除空参数
        sign_params.update(params)
        to_sign = parse.urlencode(self._params)
        sign_params.update({
            'signature': hmac.new(self._secret_key.encode(), to_sign.encode(), hashlib.sha256).hexdigest()
        })
        rsp = requests.request(method, url, params=sign_params, headers=self._headers)
        return rsp.json()

    def ping(self):
        """测试服务器连通性"""
        path = '/api/v3/ping'
        return self._unsigned_request('GET', path)

    def server_time(self):
        """获取服务器时间"""
        path = '/api/v3/time'
        return self._unsigned_request('GET', path)

    def info(self):
        """获取交易规则和交易对信息"""
        path = '/api/v3/exchangeInfo'
        return self._unsigned_request('GET', path)

    def depth(self, symbol, limit=100):
        """深度信息"""
        path = '/api/v3/depth'
        params = {
            'symbol': symbol,
            'limit': limit      # 可选值:[5, 10, 20, 50, 100, 500, 1000, 5000]
        }
        return self._unsigned_request('GET', path, params)

    def trades(self)
         """近期成交列表"""
        path = '/api/v3/trades'
        params = {
            'symbol': symbol,
            'limit': limit      # 可选值:[5, 10, 20, 50, 100, 500, 1000, 5000]
        }
        return self._unsigned_request('GET', path, params)

    def system(self):
        """系统状态"""
        path = '/wapi/v3/systemStatus.html'
        return self._signed_request('GET', path)

    def coins(self):
        """获取针对用户的所有(Binance支持充提操作的)币种信息"""
        path = '/sapi/v1/capital/config/getall'
        return self._unsigned_request('GET', path)

    def account_snapshot(self):
        """查询每日资产快照"""
        path = '/sapi/v1/accountSnapshot'
        return self._signed_request('GET', path)

    def disable_withdraw_switch(self):
        """关闭站内划转"""
        path = '/sapi/v1/account/disableFastWithdrawSwitch'
        return self._signed_request('POST', path)

    