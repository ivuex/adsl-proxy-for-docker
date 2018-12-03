# coding=utf-8
import re
import time
import requests
import asyncio
from requests.exceptions import ConnectionError, ReadTimeout
from adslproxy.db import RedisClient
from adslproxy.config import *
from adslproxy.sureprocess import sureprocess
from adslproxy.getparams import getmac, getoutip


class Sender():

    def test_proxy(self, proxy):
        """
        测试代理
        :param proxy: 代理
        :return: 测试结果
        """
        try:
            response = requests.get(TEST_URL, proxies={
                'http': 'http://' + proxy,
                'https': 'https://' + proxy
            }, timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                return True
        except (ConnectionError, ReadTimeout):
            return False

    def remove_proxy(self):
        """
        移除代理
        :return: None
        """
        self.redis = RedisClient()
        self.redis.remove(CLIENT_NAME)
        print('Successfully Removed Proxy')

    def set_proxy(self, proxy):
        """
        设置代理
        :param proxy: 代理
        :return: None
        """
        self.redis = RedisClient()
        if self.redis.set(CLIENT_NAME, proxy):
            print('Successfully Set Proxy', proxy)

    async def adsl(self):
        """
        拨号主进程
        :return: None
        """
        while True:
            print('ADSL Start, Remove Proxy, Please wait')
            self.remove_proxy()
            (status, output) = sureprocess.getstatusoutput(ADSL_BASH)
            if status == 0:
                print('ADSL Successfully')
                try:
                    ip = await getoutip()
                    if ip:
                        print('Now IP', ip)
                        print('Testing Proxy, Please Wait')
                        proxy = '{ip}:{port}'.format(ip=ip, port=PROXY_PORT)
                        if self.test_proxy(proxy):
                            print('Valid Proxy')
                            self.set_proxy(proxy)
                            print('Sleeping')
                            time.sleep(ADSL_CYCLE)
                        else:
                            print('Invalid Proxy')
                except StopIteration:
                    print('Get IP Failed, Re Dialing')
                    time.sleep(ADSL_ERROR_CYCLE)
            else:
                print('ADSL Failed, Please Check')
                time.sleep(ADSL_ERROR_CYCLE)


def run():
    sender = Sender()
    sender.adsl()


if __name__ == '__main__':
    run()
