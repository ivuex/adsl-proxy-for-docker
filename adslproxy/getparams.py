# # -*- coding:utf-8 -*-
#
import re
import requests
from adslproxy.sureprocess import sureprocess
import json
import random
from requests.exceptions import ConnectionError, ReadTimeout


async def getoutip():
    try:
        # 获取外网ip
        res = requests.get('http://httpbin.org/get')
        ip = json.loads(res.text).get('origin')
        return ip
    except(ConnectionError, ReadTimeout):
        return False


def getmac():
    # 给网卡取名，默认取docker的虚拟网卡mac,如果一个都没有匹配到就生成一个
    (status, output) = sureprocess.getstatusoutput('ifconfig docker')
    macip = ''
    if status == 0:
        pattern = re.compile('ether\s+(\w{2,4}:\w{2,4}:\w{2,4}:\w{2,4}:\w{2,4}:\w{2,4})\s+', re.S)
        match = re.search(pattern, output)
        if match:
            macip = match.group(1)
    else:
        chars = list(range(0,9)) + ['a', 'b', 'c', 'd', 'e', 'f']
        for i in list(range(0,6)):
            for j in list(range(0,4)):
                macip += random.choice(chars)
            if(i < 5):
                macip += ':'
    return macip

