import scrapy
import re
from scrapy.http import HtmlResponse
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from ..baseSpider import baseSpider
from Job.Util import StrUtil
from fake_useragent import UserAgent

ua = UserAgent()
prefs = {"profile.managed_default_content_settings.images":2}


class UNESCOjobSpider(baseSpider):
    name = "UNESCOjob"
    start_urls = []

    def __init__(self, *a, **kw):
        super(UNESCOjobSpider, self).__init__(*a, **kw)
        print("prepare to crawl UNESCO")
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('user-agent=%s' % ua.random)
        chrome_options.add_argument("test-type")
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.isHeader = {}

    def start_requests(self):
        self.driver.get("https://careers.unesco.org/careersection/1/joblist.ftl?lang=en")
        res = HtmlResponse(url='my HTML string', body=self.driver.page_source, encoding="utf-8")
        trs = res.xpath(
            '//div[@id="requisitionListInterface.listRequisitionContainer"]/table//tr[@class="ftlcopy ftlrow"]')
        print("UNESCO with [%s] jobs" % len(trs))
        simpleInfo = {}
        for i in range(0, len(trs), 1):
            work = trs[i].xpath('td[2]/div/div[1]/div[1]/div/h2/span/a/text()').extract()[0]
            self.isHeader[work] = False
            Location = trs[i].xpath('td[2]/div/div[1]/div[2]/div/span/text()').extract()[0]
            issuedate = trs[i].xpath('td[2]/div/div[1]/div[3]/span[5]/text()').extract()[0]
            ApplicationDeadline = trs[i].xpath('td[2]/div/div[1]/div[4]/span[5]/text()').extract()[0]
            simpleInfo[work] = {
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
                simpleInfo[frist_job_text]['Location'],
                simpleInfo[frist_job_text]['issuedate'],
                simpleInfo[frist_job_text]['ApplicationDeadline'])
        while True:
            values_len = len(self.isHeader)
            for v in self.isHeader.values():
                if v == True:
                    values_len -= 1
            if values_len == 0:
                self.driver.quit()
                print('UNESCO爬取结束')
                break

            self.driver.find_element_by_link_text("Next").click()
            time.sleep(2)
            res = HtmlResponse(url='my HTML string', body=self.driver.page_source, encoding="utf-8")
            work = res.xpath(
                '//span[@id="requisitionDescriptionInterface.reqTitleLinkAction.row1"]/text()'
            ).extract()[0]
            if not self.isHeader[work]:
                try:
                    self.details(
                        self.driver.page_source,
                        work,
                        simpleInfo[work]['Location'],
                        simpleInfo[work]['issuedate'],
                        simpleInfo[work]['ApplicationDeadline'])
                except:
                    print("error:岗位[%s]爬取失败" % work)
                self.isHeader[work] = True

    def details(self, page_source, work, Location, issuedate, ApplicationDeadline):
        item = self.initItem()
        item["englishname"] = "UNESCO"
        item["chinesename"] = "联合国教科文组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "法国"
        item["type"] = "科学研究"
        item["url"] = "http://en.unesco.org/"
        item["alljoburl"] = "https://careers.unesco.org/careersection/1/joblist.ftl?lang=en"
        item['joburl'] = "https://careers.unesco.org/careersection/1/joblist.ftl?lang=en"
        item["work"] = work
        item['Location'] = Location
        item['issuedate'] = issuedate
        item['ApplicationDeadline'] = ApplicationDeadline
        res = HtmlResponse(url='my HTML string', body=page_source, encoding="utf-8")
        selector = scrapy.Selector(res)
        divs = selector.xpath('//div[@class="editablesection"]/div')
        item["PostLevel"] = divs[3].xpath('span[5]/text()').extract()[0].strip('-')
        item["belong"] = divs[4].xpath('span[4]/text()').extract()[0]
        item["full_time"] = divs[7].xpath('span[5]/text()').extract()[0]
        item["description"] = self.tostring(divs[15].xpath('string(.)').extract()[0])
        __ = StrUtil.delMoreSpace(divs[19].xpath('string(.)').extract()[0])
        try:
            item["education"] = re.search(r'EDUCATION(.*?)WORK(\s+)EXPERIENCE', __, re.I).group(1)
            try:
                item["experience"] = re.search(r'WORK(\s+)EXPERIENCE(.*?)SKILLS/COMPETENCIES', __, re.I).group(2)
                item["skill"] = re.search(r'SKILLS/COMPETENCIES(.*?)LANGUAGES', __, re.I).group(1)
            except:
                item["experience"] = re.search(r'WORK(\s+)EXPERIENCE(.*?)Skills and competencies', __, re.I).group(2)
                item["skill"] = re.search(r'Skills and competencies(.*?)LANGUAGES', __, re.I).group(1)
            item["language"] = re.search(r'LANGUAGES(.*)', __, re.I).group(1)
        except:
            item["education"] = re.search(r'ETUDES(.*?)EXPERIENCE(\s+)PROFESSIONNELLE', __, re.I).group(1)
            item["experience"] = re.search(
                r'EXPERIENCE(\s+)PROFESSIONNELLE(.*?)APTITUDES/COMPETENCES', __, re.I
            ).group(2)
            item["skill"] = re.search(r'APTITUDES/COMPETENCES(.*?)LANGUES', __, re.I).group(1)
            item["language"] = re.search(r'LANGUES(.*)', __, re.I).group(1)
        self.debugItem(item)
        self.insert(item)
