

import scrapy
from ..baseSpider import baseSpider
from scrapy.http import Request


class CERNjobsSpider(baseSpider):
    name = 'CERNjob'
    start_urls = [
        'http://jobs.web.cern.ch/latest-jobs?page=0']
    
    def __init__(self,*a, **kw):
        super(CERNjobsSpider, self).__init__(*a, **kw)
        print('开始爬取CERN岗位信息')

    def parse(self, response):
        selector = scrapy.Selector(response)
        links = selector.xpath("//table[@class='views-view-grid cols-1']/tbody/tr/td/div[1]/span/a/@href").extract()
        print('CERN共有[%s]条岗位待爬'%len(links))
        for link in links:
            print('开始爬取[%s]' % link)
            yield Request(url=link, callback=self.parseDetials)

    def parseDetials(self, response):
        '''
        页面提取器，解析字段
        '''
        item = self.initItem()
        selector = scrapy.Selector(response)
        item['joburl'] = response.url
        item['incontinent'] = '欧洲'
        item['alljoburl'] = 'http://jobs.web.cern.ch/content/join-us'
        item['type'] = '物理'
        item['englishname'] = 'CERN'
        item['chinesename'] = '欧洲核子国际组织'
        item['url'] = 'https://home.cern/'
        item['incountry'] = '瑞士'
        con = selector.xpath("//div[@class='views-row views-row-1 views-row-odd views-row-first views-row-last']")
        item["belong"] = con[1].xpath('div[3]/div/text()').extract()[0] if con[1].xpath('div[3]/div/text()').extract() else ""
        item["PostLevel"] = con[1].xpath('div[5]/div/text()').extract()[0] if con[1].xpath('div[5]/div/text()').extract() else ""
        item["contracttime"] = con[1].xpath('div[@class="views-field views-field-nothing"]/span[2]/text()').extract()[0] if \
        con[1].xpath('div[@class="views-field views-field-nothing"]/span[2]/text()').extract() else ""
        item['work'] = con[0].xpath("div[@class='views-field views-field-title']/span/h1/text()").extract()[0]
        item['issuedate'] = con[0].xpath("div[@class='views-field views-field-field-job-pub-date']/div/span/text()").extract()[0]
        item['ApplicationDeadline'] = con[0].xpath("div[@class='views-field views-field-field-job-date-closed']/div/span/text()").extract()[0]
        if con[0].xpath("div[@class='views-field views-field-field-job-intro-en']").xpath('string(.)').extract():
            item['description'] = self.tostring(con[0].xpath("div[@class='views-field views-field-field-job-intro-en']").xpath('string(.)').extract()[0])
        elif con[0].xpath("div[@class='views-field views-field-field-job-progr-role-descr-en']").xpath('string(.)').extract():
            item['description'] = self.tostring(con[0].xpath("div[@class='views-field views-field-field-job-progr-role-descr-en']").xpath('string(.)').extract()[0])
        else:item['description'] = self.tostring(con[0].xpath('div[@class="views-field views-field-field-job-descr"]').xpath('string(.)').extract()[0])
        try:item['responsibilities'] = self.tostring(con[0].xpath('div[@class="views-field views-field-field-job-function-en"]').xpath('string(.)').extract()[0])
        except:pass
        _ = con[0].xpath("div[@class='views-field views-field-field-job-qualification-en']/div[@class='field-content']").xpath('string(.)').extract()
        if _:item['education'] = self.tostring(_[0])
        else:item['education'] = "bachelor"
        _ = con[0].xpath('div[@class="views-field views-field-field-job-experience-en"]/div//ul')
        if _:
            if len(_) == 4:
                item['experience'] = self.tostring(_[0].xpath('string(.)').extract()[0] + _[2].xpath('string(.)').extract()[0])
                item['skill'] = self.tostring(_[1].xpath('string(.)').extract()[0])
                item['language'] = self.tostring(_[3].xpath('string(.)').extract()[0])
            elif len(_) == 5:
                item['experience'] = self.tostring(_[0].xpath('string(.)').extract()[0] + _[2].xpath('string(.)').extract()[0] +\
                                                   _[3].xpath('string(.)').extract()[0])
                item['skill'] = self.tostring(_[1].xpath('string(.)').extract()[0])
                item['language'] = self.tostring(_[4].xpath('string(.)').extract()[0])
        else:
            _ = con[0].xpath('div[@class="views-field views-field-field-job-eligibility-en"]/div/ul').xpath('string(.)').extract()
            if _:item['education'] = item['language'] = item['experience'] = item['skill'] = self.tostring(_[0])
            else:item['education'] = item['language'] = item['experience'] = item['skill'] = \
                    self.tostring(con[0].xpath('div[@class="views-field views-field-field-job-eligibility-en"]/div').xpath('string(.)').extract()[0])
        self.debugItem(item)
        # self.insert(item)