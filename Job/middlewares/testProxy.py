import threading
import requests


class testProxy(threading.Thread):
    def __init__(self, proxyMiddleware, part):
        super(testProxy, self).__init__()
        self.proxyMiddleware = proxyMiddleware
        self.part = part

    def run(self):
        self.test_proxyes(self.part)

    def test_proxyes(self, proxyes):
        '''
        检测代理ip是否可用，可用则修改ip标识为Ture
        :param proxyes: 代理ip
        '''
        for proxy, valid in proxyes.items():
            if (self.check_proxy(proxy)):
                self.proxyMiddleware.proxyes[proxy] = True
                self.proxyMiddleware.append_proxy(proxy)

    def check_proxy(self, proxy):
        '''检测代理是否可用'''
        try:
            resbody = requests.get(self.proxyMiddleware.test_urls, proxies={"http": proxy}, timeout=self.proxyMiddleware.test_proxy_timeout)
            if resbody.status_code != 200:
                print("IP:http://%s不可用" % proxy)
                return False
            print("IP:http://%s可用" % proxy)
            return True
        except Exception:
            print("IP:http://%s不可用" % proxy)
            return False
