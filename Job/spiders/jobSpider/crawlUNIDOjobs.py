
import scrapy
from scrapy.http import Request
from Job.Util import StrUtil
from ..baseSpider import baseSpider


class UNIDOjobLink(baseSpider):
    name = "UNIDOjob"
    start_urls = ["http://www.unido.org/employment/consultancy-opportunities.html",
                  "http://www.unido.org/employment/o518900.html",
                  "http://www.unido.org/overview/employment/internship.html",
                  "http://www.unido.org/internship/internships-in-field-offices.html"]

    def __init__(self,*a, **kw):
        super(UNIDOjobLink, self).__init__(*a, **kw)
        self.preurl = 'http://www.unido.org'

    def parse(self, response):
        cnt = 0
        selector = scrapy.Selector(response)
        joburls = selector.xpath('//li[@class="active current activeandsub"]/ul/li/a')

        if response.url == 'http://www.unido.org/internship/internships-in-field-offices.html':
            others = selector.xpath('//div[@class="csc-textpic-text"]/div/table/tbody/tr/td/a')
            for other in others[1:]:
                finalurl = other.xpath('@href').extract()[0]
                if finalurl.endswith('.pdf'):
                    url = self.preurl + finalurl
                    yield Request(url, callback=self.duepdf, dont_filter=True)
                else:
                    pass
        else:
            try:
                for joburl in joburls:
                    url = self.preurl + joburl.xpath('@href').extract()[0]
                    cnt += 1
                    print('正在抓取<---  ' + url)
                    yield Request(url=url, callback=self.wr)
            except:
                pass
            print("%s" % response.url + '->>共有'+ str(cnt) + '个招聘信息')

    def wr(self,response):
        selector = scrapy.Selector(response)
        deeps = selector.xpath('//li[@class="active current activeandsub"]/ul/li/a')
        if deeps:
            for deep in deeps:
                url = self.preurl + deep.xpath('@href').extract()[0]
                yield Request(url, callback=self.wr)
            return

        if response.url == 'http://www.unido.org/internship/internships-in-field-offices.html':
            return

        item = self.initItem()
        item['englishname'] = 'UNIDO'  # 组织英文缩写
        item['chinesename'] = '联合国工业发展组'  # 组织中文缩写
        item['incontinent'] = '欧洲'  # 组织所属洲
        item['incountry'] = '奥地利'  # 组织所在国家
        item['type'] = '经济'  # 组织类别
        item['url'] = 'www.unido.org'  # 组织主页
        item['alljoburl'] = 'http://www.unido.org/employment.html'
        url = response.url
        item['joburl'] = url
        num = 0

        main_content = selector.xpath('//div[@class="csc-default"]/p')
        itemname = ''
        text = ''
        tips = ''
        totle = 0
        for i in main_content:
            totle += 1

        while num < totle:
            target = ''
            content = main_content[num]
            try:
                target = content.xpath('b/text()').extract()[0]
                text = content.xpath('text()').extract()[0]
            except:
                pass
            num += 1
            if target == 'Duration:' or target == 'Duration: ':
                itemname = 'ExpectedDurationofAssignment'
            elif target == 'Duty Station:' or target == 'Duty Station: ':
                itemname = 'Location'
            elif target == 'Tasks:' or target == 'Tasks: ':
                itemname = 'responsibilities'
                num2 = num
                for content in main_content[num2:]:
                    target = content.xpath('b/text()')
                    if not target:
                        num += 1
                        text += content.xpath('text()').extract()[0]
                    else:
                        break
            elif target == 'Qualification requirements:' or target == 'Qualification requirements: ':
                num2 = num
                for content in main_content[num2:]:
                    test = content.xpath('text()').extract()[0]
                    if 'Education' in test:
                        item['education'] = test
                    elif 'Experience' in test:
                        item['experience'] = test
                    elif 'Language' in test:
                        item['language'] = test
                break
            else:
                try:
                    cont = content.xpath('b')
                    tips += cont.xpath('string(.)').extract()[0]
                except:
                    pass
                continue

            item[itemname] = StrUtil.delWhiteSpace(text)
            print("UNIDO-->job-->%s" % url+'-->'+itemname+'-->'+item[itemname])

        Work = selector.xpath('//div[@id="header-content"]/div/h1/text()').extract()[0]
        item['work'] = StrUtil.delWhiteSpace(Work)
        print("UNIDO-->job-->%s" % url+'-->Work-->'+item['work'])

        itemname= 'addition'
        item[itemname] = StrUtil.delWhiteSpace(tips)
        print("UNIDO-->job-->%s" % url + '-->' + itemname + '-->' + item[itemname])
        self.insert(item)

    def duepdf(self, response):
        url = response.url
        items = self.initItem()
        items['joburl'] = url
        if url.endswith('.pdf'):
            PDF_name = url.split('/')[-1]
            items['work'] = StrUtil.delWhiteSpace(PDF_name)
            print("UNIDO-->job-->%s" % items['work'])
            yield Request(url, meta={'items': items}, callback=self.savepdf, dont_filter=True)
        else:
            items['addition'] = StrUtil.delWhiteSpace(url)
        self.insert(items)

    def savepdf(self, response):
        items = response.meta['items']
        with open('./UNIDOPDF/' + items['work'], 'wb') as f:
            f.write(response.body)


