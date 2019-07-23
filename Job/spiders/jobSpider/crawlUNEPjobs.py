import scrapy

try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup
import re
from ..baseSpider import baseSpider
from Job.Util import StrUtil
from scrapy import Request


class UNEPJobSpider(baseSpider):
    name = 'UNEPjob'
    start_urls = ['https://www.unenvironment.org/work-with-us?title=&field_category_tid=All&division=All']

    def __init__(self, *a, **kw):
        print("prepare to crawl UNEP")
        super(UNEPJobSpider, self).__init__(*a, **kw)

    def parse(self, response):
        selector = scrapy.Selector(response)
        pageLinks = selector.xpath('//div[@class="result_item_title"]/h5/a/@href')
        for eachLink in pageLinks:
            url = eachLink.extract()
            yield Request(url=url, callback=self.parseJob, dont_filter=True)

    def parseJob(self, res):
        selector = scrapy.Selector(res)
        item = self.initItem()
        item['joburl'] = res.url
        item['incontinent'] = '非洲'
        item['alljoburl'] = 'https://www.unenvironment.org/work-with-us?title=&field_category_tid=All&division=All'
        item['type'] = '环境'
        item['englishname'] = 'UNEP'
        item['url'] = 'http://www.unep.org/'
        item['incountry'] = '肯尼亚'
        item['chinesename'] = '联合国环境计划署'
        trs = selector.xpath('//table[@id="JobDescription"]/tr')
        title = trs[0].xpath('td[2]/span/text()').extract()[0]
        item["work"] = title
        item["PostLevel"] = re.search(r'[PDG]\d', item["work"], re.I).group(0)
        item["belong"] = trs[2].xpath('td[2]/span/text()').extract()[0]
        item["Location"] = trs[3].xpath('td[2]/span/text()').extract()[0]
        time = trs[4].xpath('td[2]/span/text()').extract()[0]
        item["issuedate"] = time.split('-')[0]
        item["ApplicationDeadline"] = time.split('-')[1]
        text = StrUtil.delMoreSpace(
            StrUtil.delWhiteSpace(selector.xpath('//div[@id="jd_content"]').xpath('string(.)').extract()[0]))
        item["responsibilities"] = re.search(r'Responsibilities(.*)Competencies', text).group(1)
        if re.search(r'Special\s+Notice(.*)Org\.\s+Setting\s+and\s+Reporting', text) != None:
            item["description"] = re.search(r'Special\s+Notice(.*)Org\.\s+Setting\s+and\s+Reporting', text).group(1)
        else:
            item["description"] = re.search(r'Special\s+Notice(.*)United\s+Nations\s+Considerations', text).group(1)
        item["skill"] = re.search(r'Competencies(.*)Education', text).group(1)
        item["education"] = re.search(r'Education(.*)Work\s+Experience', text).group(1)
        item["experience"] = re.search(r'Work\s+Experience(.*)Languages', text).group(1)
        item["language"] = re.search(r'Languages(.*)Assessment', text).group(1)
        item["addition"] = re.search(r'United\s+Nations\s+Considerations(.*?)No\s+Fee', text).group(1)
        self.debugItem(item)
        self.insert(item)
