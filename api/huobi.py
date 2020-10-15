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


class HuobiClient(object):
    def __init__(self, **kwargs):
        self._api_key = kwargs.get("api_key", None)
        self._secret_key = kwargs.get("secret_key", None)
        self._server_url = 'https://api.huobi.pro'
        self._headers = {'Content-Type': 'application/json'}

    def _unsigned_request(self, method, path, params=None):
        """无签名访问"""
        url = path if path.startswith('https') else self._server_url + path
        rsp = requests.request(method, url, params=params)
        return rsp.json()

    def _signed_request(self, method, path, params={}):
        """带签名访问"""
        url = self._server_url + path
        sign_params = {
            'AccessKeyId': self._api_key,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        }
        params = {f'{x}': params[x] for x in params if params[x]}  # 去除空参数
        if method == 'GET' and params:
            sign_params.update(params)
        target = sorted(sign_params.items(), key=lambda x: x[0], reverse=False)  # 参数ASCII排序
        to_sign = '\n'.join([method, 'api.huobi.pro', path, parse.urlencode(target)])
        sign_params.update({
            'Signature': base64.b64encode(hmac.new(self._secret_key.encode(), to_sign.encode(), hashlib.sha256).digest()).decode()
        })
        if method == 'POST':
            rsp = requests.request(method, url + '?' + parse.urlencode(sign_params),
                                        data=json.dumps(params), headers=self._headers)
        else:
            rsp = requests.request(method, url, params=sign_params, headers=self._headers)
        return rsp.json()

    def system_status(self):
        """获取当前系统状态"""
        path = 'https://status.huobigroup.com/api/v2/summary.json'
        return self._unsigned_request('GET', path)

    def market_status(self):
        """获取当前市场状态"""
        path = '/v2/market-status'
        return self._unsigned_request('GET', path)

    def symbols(self):
        """获取所有交易对"""
        path = '/v1/common/symbols'
        return self._unsigned_request('GET', path)

    def common_currencies(self):
        """获取所有币种"""
        path = '/v1/common/currencys'
        return self._unsigned_request('GET', path)

    def reference_currencies(self, currency=None, auth=False):
        """币链参考信息"""
        path = '/v2/reference/currencies'
        params = {
            'currency': currency,
            'authorizedUser': auth 
        }
        return self._unsigned_request('GET', path, params)

    def timestamp(self):
        """获取当前系统时间戳"""
        path = '/v1/common/timestamp'
        return self._unsigned_request('GET', path)

    def klines(self, symbol, period, size=150):
        """K 线数据（蜡烛图）"""
        path = '/market/history/kline'
        params = {
            'symbol': symbol,  # btcusdt, ethbtc, btc3lusdtnav等
            'period': period,  # 1min, 5min, 15min, 30min, 60min, 4hour, 1day, 1mon, 1week, 1year
            'size': size
        }
        return self._unsigned_request('GET', path, params)

    def ticker(self, symbol):
        """聚合行情（Ticker）"""
        path = '/market/detail/merged'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def tickers(self):
        """所有交易对的最新 Tickers"""
        path = '/market/tickers'
        return self._unsigned_request('GET', path)

    def depth(self, symbol, depth=20, type_='step0'):
        """市场深度数据"""
        path = '/market/depth'
        params = {
            'symbol': symbol,
            'depth': depth,     # 5, 10, 20
            'type': type_       # step0，step1，step2，step3，step4，step5
        }
        return self._unsigned_request('GET', path, params)

    def trade(self, symbol):
        """最近市场成交记录"""
        path = '/market/trade'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def trades(self, symbol, size=1):
        """获得近期交易记录"""
        path = '/market/history/trade'
        params = {
            'symbol': symbol,
            'size': size
        }
        return self._unsigned_request('GET', path, params)

    def detail_24h(self, symbol):
        """最近24小时行情数据"""
        path = '/market/detail'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def etp(self, symbol):
        """获取杠杆ETP实时净值"""
        path = '/market/etp'
        params = {
            'symbol': symbol
        }
        return self._unsigned_request('GET', path, params)

    def account(self):
        """账户信息"""
        path = '/v1/account/accounts'
        return self._signed_request('GET', path)

    def balance(self, account_id):
        """账户余额"""
        path = f'/v1/account/accounts/{account_id}/balance'
        return self._signed_request('GET', path)

    def asset_valuation(self, account_type, currency='BTC', subuid=None):
        """获取账户资产估值"""
        path = '/v2/account/asset-valuation'
        params = {
            'accountType': account_type,    # spot：现货账户， margin：逐仓杠杆账户，otc：OTC 账户，super-margin：全仓杠杆账户
            'valuationCurrency': currency,  # 可选法币有：BTC、CNY、USD、JPY、KRW、GBP、TRY、EUR、RUB、VND、HKD、TWD、MYR、SGD、AED、SAR （大小写敏感）
            'subUid': subuid                # 子用户的 UID，若不填，则返回API key所属用户的账户资产估值
        }
        return self._signed_request('GET', path, params)

    def transfer(self, from_uid, from_type, from_aid, to_uid, to_type, to_aid, currency, amount):
        """资产划转"""
        path = '/v1/account/transfer'
        params = {
            'from-user': from_uid,              # 母用户uid,子用户uid
            'from-account-type': from_type,     # spot,margin
            'from-account': from_aid,           # account id
            'to-user': to_uid,                  # 母用户uid,子用户uid
            'to-account-type': to_type,         # spot,margin
            'to-account': to_aid,               # account id
            'currency': currency,
            'amount': amount
        }
        return self._signed_request('POST', path, params)

