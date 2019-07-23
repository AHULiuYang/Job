import scrapy
from ..baseSpider import baseSpider
import re
from scrapy.http import HtmlResponse
import requests
from Job.Util import TimeUtil


class ESCAPjobsSpider(baseSpider):
    name = 'ESCAPjob'
    start_urls = ["http://www.unescap.org/jobs"]

    def __init__(self, *a, **kw):
        super(ESCAPjobsSpider, self).__init__(*a, **kw)
        print("prepare to crawl ESCAP")

    def parse(self, response):
        selector = scrapy.Selector(response)
        links = selector.xpath('//div[@class="attachment attachment-before"]//a')

        for _ in links:
            link = _.xpath('@href').extract()[0]
            if ".pdf" in link:
                print('pdf格式文件无法爬取[%s]' % link)
                continue
            print('准备爬取链接[%s]' % link)
            r = requests.get(link)
            self.parseBody(r, link)

    def parseBody(self, r, link):
        selector = HtmlResponse(url="my HTML string", body=r.text, encoding="utf-8")
        _ = {
            'Posting Title:': 'work',
            'Department/ Office:': 'belong',
            'Duty Station:': 'Location',
            'Posting Period:': 'time',
        }
        item = self.initItem()
        item['incontinent'] = '亚洲'
        item['joburl'] = link
        item['alljoburl'] = 'http://www.unescap.org/jobs'
        item['type'] = '经济'
        item['englishname'] = 'ESCAP'
        item['chinesename'] = '亚太经社会'
        item['url'] = 'http://www.unescap.org/'
        item['incountry'] = '泰国'
        trs = selector.xpath('//div[@id="win0div$ICField3$0"]/table[@class="PABACKGROUNDINVISIBLE"]//tr')[1:]
        for i in range(0, len(trs), 2):
            try:
                k = trs[i].xpath('td[2]/div/span/text()').extract()[0]
                if k in _.keys():
                    item[_[k]] = self.tostring(trs[i + 1].xpath('td[2]/div/span/text()').extract()[0])
                else:
                    continue
            except:
                k = trs[i].xpath('td[2]/div/label/text()').extract()[0]
                if k in _.keys():
                    item[_[k]] = self.tostring(trs[i + 1].xpath('td[2]/div/span/text()').extract()[0])
                else:
                    continue
        item['PostLevel'] = re.search(r'[DPG][0-9]', item['work']).group(0)
        issuedate = item['time'].split('-')[0].split()[::-1]
        issuedate[1] = TimeUtil().month[issuedate[1].lower()]
        item['issuedate'] = "/".join(issuedate)
        ApplicationDeadline = item['time'].split('-')[1].split()[::-1]
        ApplicationDeadline[1] = TimeUtil().month[ApplicationDeadline[1].lower()]
        item['ApplicationDeadline'] = "/".join(ApplicationDeadline)

        texts = selector.xpath('//div[@id="win0divHRS_JO_PST_DSCR$0"]/table[@class="PABACKGROUNDINVISIBLE"]//tr')[2:]
        __ = {
            'Responsibilities': 'responsibilities',
            'Qualifications/special skills': 'skill',
            'Education': 'education',
            'Work Experience': 'experience',
            'Languages': 'language',
            'United Nations Considerations': 'addition',
            'Org. Setting and Reporting': 'description'
        }
        for i in range(0, len(texts), 4):
            k = texts[i].xpath('td[2]/div/span/text()').extract()[0]
            if k in __.keys():
                item[__[k]] = self.tostring(texts[i + 2].xpath('string(.)').extract()[0])
            else:
                continue
        self.debugItem(item)
        self.insert(item)
