import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
from ..baseSpider import baseSpider
import re
from fake_useragent import UserAgent

ua = UserAgent()
prefs = {"profile.managed_default_content_settings.images": 2}


class OECDJobSpider(baseSpider):
    name = 'OECDjob'
    start_urls = []

    def __init__(self, *a, **kw):
        super(OECDJobSpider, self).__init__(*a, **kw)
        print("prepare to crawl OECD")
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('user-agent=%s' % ua.random)
        chrome_options.add_argument("test-type")
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.isHeader = {}

    def start_requests(self):
        self.driver.get("https://oecd.taleo.net/careersection/ext/joblist.ftl")
        res = HtmlResponse(url='my HTML string', body=self.driver.page_source, encoding="utf-8")
        trs = res.xpath(
            '//div[@id="requisitionListInterface.listRequisitionContainer"]/table//tr[@class="ftlcopy ftlrow"]')
        print("OECD共有%s条岗位数据待爬" % len(trs))
        simpleInfo = {}
        for i in range(0, len(trs), 1):
            work = trs[i].xpath('td[2]/div/div[1]/div[1]/div/h2/span/a/text()').extract()[0]
            self.isHeader[work] = False
            belong = trs[i].xpath('td[2]/div/div[1]/div[2]/span[1]/text()').extract()
            belong = belong[0] if belong else ""
            Location = trs[i].xpath('td[2]/div/div[1]/div[2]/div/span/text()').extract()[0]
            issuedate = trs[i].xpath('td[2]/div/div[1]/div[3]/span[3]/text()').extract()[0]
            ApplicationDeadline = trs[i].xpath('td[2]/div/div[1]/div[4]/span[3]/text()').extract()[0]
            simpleInfo[work] = {
                'belong': belong,
                'Location': Location,
                'issuedate': issuedate,
                'ApplicationDeadline': ApplicationDeadline
            }
        frist_job_text = res.xpath('//a[@id="requisitionListInterface.reqTitleLinkAction.row1"]/text()').extract()[0]
        self.driver.find_element_by_link_text(frist_job_text).click()
        if frist_job_text in self.driver.page_source:
            self.isHeader[frist_job_text] = True
            self.details(
                self.driver.page_source,
                frist_job_text,
                simpleInfo[frist_job_text]['belong'],
                simpleInfo[frist_job_text]['Location'],
                simpleInfo[frist_job_text]['issuedate'],
                simpleInfo[frist_job_text]['ApplicationDeadline'])
        while True:
            self.driver.find_element_by_link_text("Next").click()
            res = HtmlResponse(url='my HTML string', body=self.driver.page_source, encoding="utf-8")
            work = res.xpath('//span[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]/text()').extract()[
                0]
            if not self.isHeader[work]:
                try:
                    self.details(
                        self.driver.page_source,
                        work,
                        simpleInfo[work]['belong'],
                        simpleInfo[work]['Location'],
                        simpleInfo[work]['issuedate'],
                        simpleInfo[work]['ApplicationDeadline'])
                except:
                    print("error:%s" % work)
                self.isHeader[work] = True
            if not False in self.isHeader.values():
                self.driver.quit()
                print('OECD爬取结束')
                break

    def details(self, page_source, work, belong, Location, issuedate, ApplicationDeadline):
        item = self.initItem()
        item["englishname"] = "OECD"
        item["chinesename"] = "经济合作与发展组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "法国"
        item["type"] = "经济"
        item["url"] = "http://www.oecd.org/"
        item["alljoburl"] = "https://oecd.taleo.net/careersection/ext/joblist.ftl"
        item['joburl'] = "https://oecd.taleo.net/careersection/ext/joblist.ftl"
        item["work"] = work
        item['belong'] = belong
        item['Location'] = Location
        item['issuedate'] = issuedate
        item['ApplicationDeadline'] = ApplicationDeadline
        res = HtmlResponse(url='my HTML string', body=page_source, encoding="utf-8")
        selector = scrapy.Selector(res)

        def getInfo(k, v):
            try:
                item[k] = v.group(1)
                if k == 'education':
                    item[k] = v.group(2)
            except:
                print(u'字段解析出错:' + k)

        data = self.tostring(selector.xpath('//div[@class="ftllist"]/table').xpath('string(.)').extract_first())
        getInfo('description', re.match(r'(.*)([Mm]ain [Rr]esponsibilities)|(Date and time)', data))
        getInfo('responsibilities',
                re.search(r'[Mm]ain\s+[Rr]esponsibilities(.*)[Ideal](.|\s){,50}\s+[Pp]rofile', data))
        getInfo('education', re.search(r'[Ideal](.|\s){,50}\s+[Pp]rofile(.*?)[Ll]anguages', data))
        getInfo('language', re.search(r'[Ll]anguages(.*?)[Cc]ore [Cc]ompetencies', data))
        getInfo('skill', re.search(r'[Cc]ore [Cc]ompetencies(.*?)[Cc]ontract [Dd]uration', data))
        getInfo('contracttime', re.search(r'[Cc]ontract [Dd]uration(.*?)[Ww]hat [Tt]he OECD [Oo]ffers', data))
        self.debugItem(item)
        self.insert(item)
