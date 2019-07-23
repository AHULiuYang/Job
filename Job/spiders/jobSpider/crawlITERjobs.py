import scrapy

try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup
from selenium import webdriver
from ..baseSpider import baseSpider
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

ua = UserAgent()
prefs = {"profile.managed_default_content_settings.images": 2}


class ITERJobSpider(baseSpider):
    name = 'ITERjob'
    start_urls = ["http://www.iter.org/jobs"]

    def __init__(self, *a, **kw):
        super(ITERJobSpider, self).__init__(*a, **kw)
        print("prepare to crawl ITER")
        # self.driver = webdriver.PhantomJS()
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('user-agent=%s' % ua.random)
        chrome_options.add_argument("test-type")
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome()

        self.matchingDict = {'work': 'Jobtitle',
                             'belong': 'Department',
                             'ApplicationDeadline': 'Application Deadline (MM/DD/YYYY)',
                             'PostLevel': 'Grade',
                             'responsibilities': 'Main duties / Responsibilities',
                             'description': 'Purpose',
                             'education': ['Level of study', 'Diploma'],
                             'experience': ['Level of experience', 'Technical experience/knowledge'],
                             'skill': ['Social skills', 'Specific skills', 'General skills'],
                             'addition': 'Others',
                             'language': 'Languages'}

    def parse(self, response):

        selector = scrapy.Selector(response)
        for tr in selector.xpath('//table[@class="table"]/tr')[1:]:
            link = tr.xpath('td[1]/a/@href').extract()[0]
            print("准备爬取%s" % link)
            self.driver.get(link)
            item = self.initItem()
            item['joburl'] = link
            item['incontinent'] = '欧洲'
            item['alljoburl'] = 'http://www.iter.org/jobs'
            item['type'] = '能源'
            item['englishname'] = 'ITER'
            item['chinesename'] = '国际热核聚变实验堆计划'
            item['url'] = 'http://www.iter.org/proj/inafewlines#5'
            item['incountry'] = '法国'
            itemDict = self.crawlJobDetailPage(self.driver.page_source)

            # todo 整理字段,导入新定义的item
            for each in self.matchingDict.keys():
                if isinstance(self.matchingDict[each], str):
                    if self.matchingDict.get(each) in itemDict.keys():
                        item[each] = itemDict[self.matchingDict.get(each)]
                elif isinstance(self.matchingDict[each], list):
                    for _ in self.matchingDict.get(each):
                        if _ in itemDict.keys():
                            item[each] += itemDict[_]
            self.debugItem(item)
            self.insert(item)

    def crawlJobDetailPage(self, res):
        soup = BeautifulSoup(res, 'html.parser')
        tr = soup.find('div', id='subform').find('table').find('tbody').find_all('tr')
        item = {}
        item['Division'] = ""
        item['Diploma'] = ""
        item['Others'] = ""
        item['Jobtitle'] = tr[0].find('td').find('h3').find('span').text
        trs = tr[1].find('td').find('table').find('tbody').find_all('tr')
        for t in trs:
            try:
                td = t.find_all('td')
                key = td[0].find('div').find('span').text
                value = td[1].find('span').text
                item[key] = value
            except:
                pass
        return item
