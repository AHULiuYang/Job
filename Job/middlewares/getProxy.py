from bs4 import BeautifulSoup
import threading
import requests

class getProxy(threading.Thread):

    def __init__(self, proxyes, url):
        super(getProxy, self).__init__()
        '''
        >>>self.proxyes[proxy]
            True:校验成功
            False：未检验
        '''
        self.proxyes = proxyes
        self.url = url

    def run(self):
        self.proxyes.update(getattr(self, 'fecth_proxy_from_' + self.url)())

    def fecth_proxy_from_xici(self):
        '''
        爬取西刺网代理
        :return: 代理
                >>>proxyes
                >>>{'http://61.224.170.55:8088':False}
        '''
        proxyes = {}
        url = "http://www.xicidaili.com/nn/"
        try:
            for i in range(1, 2):
                soup = self.get_soup(url + str(i))
                trs = soup.find("table", attrs={"id": "ip_list"}).find_all("tr")
                for i, tr in enumerate(trs):
                    if(0 == i):
                        continue
                    tds = tr.find_all('td')
                    ip = tds[1].text
                    port = tds[2].text
                    proxy = ''.join(['http://', ip, ':', port]).encode('utf-8')
                    proxyes[proxy] = False
        except Exception as e:
            print('从西刺网爬取IP出现异常[%s]', e)
        return proxyes

    def fecth_proxy_from_ip3336(self):
        '''
        爬取ip3306代理网站ip
        :return: 代理
                >>>proxyes
                >>>{'http://61.224.170.55:8088':False}
        '''
        proxyes = {}
        url = 'http://www.ip3366.net/free/?stype=1&page='
        try:
            for i in range(1, 6):
                soup = self.get_soup(url + str(i))
                trs = soup.find("div", attrs={"id": "list"}).table.find_all("tr")
                for i, tr in enumerate(trs):
                    if 0 == i:
                        continue
                    tds = tr.find_all("td")
                    ip = tds[0].string.strip()
                    port = tds[1].string.strip()
                    proxy = ''.join(['http://', ip, ':', port])
                    proxyes[proxy] = False
        except Exception as e:
            print('从ip3336爬取IP出现异常[%s]', e)
        return proxyes

    def get_soup(self, url):
        '''
        使用beautiful解析代理网页
        :param url: 代理链接
        :return: beautiful对象
        '''
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc,"lxml")
        return soup
