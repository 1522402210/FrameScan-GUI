#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
name: Moxa OnCell 未授权访问
referer: unknown
author: Lucifer
description: Moxa OnCell telnet直接进入。
'''
import sys
import warnings
import telnetlib

from urllib.parse import urlparse

class moxa_oncell_telnet_BaseVerify:
    def __init__(self, url):
        self.url = url

    def run(self):
        result = ['Moxa OnCell 未授权访问', '', '']
        port = 23
        if r"http" in self.url:
            #提取host
            host = urlparse(self.url)[1]
            try:
                port = int(host.split(':')[1])
            except:
                pass
            flag = host.find(":")
            if flag != -1:
                host = host[:flag]
        else:
            if self.url.find(":") >= 0:
                host = self.url.split(":")[0]
                port = int(self.url.split(":")[1])
            else:
                host = self.url

        try:
            #连接Telnet服务器
            tlib = telnetlib.Telnet(host, port, timeout=6)
            #tlib.set_debuglevel(2)
            #登陆
            result = tlib.read_until(b"Console terminal type", timeout=6)
            tlib.close()
            if result.find(b"Console terminal type") is not -1:
                result[2] = '存在'
                result[1]=host+":"+str(port)
            else:
                result[2] = '不存在'

        except:
            result[2] = '未知'
        return result

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    testVuln = moxa_oncell_telnet_BaseVerify(sys.argv[1])
    testVuln.run()