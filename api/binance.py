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
        rsp = requests.request(method, url, params=params, headers=self._headers)
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

    def trades(self, symbol, limit=500):
        """近期成交列表"""
        path = '/api/v3/trades'
        params = {
            'symbol': symbol,
            'limit': limit      # 可选值:[5, 10, 20, 50, 100, 500, 1000, 5000]
        }
        return self._unsigned_request('GET', path, params)

    def history(self, symbol, limit=500, fromId=None):
        """查询历史成交"""
        path = '/api/v3/historicalTrades'
        params = {
            'symbol': symbol,
            'limit': limit,     # 默认 500; 最大值 1000.
            'fromId': fromId    # 从哪一条成交id开始返回. 缺省返回最近的成交记录。
        }
        return self._unsigned_request('GET', path, params)

    def agg_trades(self, symbol, fromId=None, start_time=None, end_time=None, limit=500):
        """近期成交(归集)"""
        path = '/api/v3/aggTrades'
        params = {
            'symbol': symbol,
            'fromId': fromId,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit
        }
        return self._unsigned_request('GET', path, params)

    def klines(self, symbol, interval, start_time=None, end_time=None, limit=500):
        """K线数据
        interval: 1/3/5/15/30m,1/2/4/6/8/12h,1/3d,1w,1M
        """
        path = '/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit
        }
        return self._unsigned_request('GET', path, params)

    def avg_price(self, symbol):
        """当前平均价格"""
        path = '/api/v3/avgPrice'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def ticker_24hr(self, symbol=None):
        """24hr 价格变动情况"""
        path = '/api/v3/ticker/24hr'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def ticker_price(self, symbol=None):
        """最新价格"""
        path = '/api/v3/ticker/price'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def ticker_book(self, symbol=None):
        """当前最优价格"""
        path = '/api/v3/ticker/bookTicker'
        params = {
            'symbol': symbol
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

    