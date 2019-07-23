import re

from Job.Util import StrUtil
from ..baseSpider import baseSpider
import scrapy
from scrapy_splash import SplashRequest


class WIPOjobSpider(baseSpider):
    name = "WIPOjob"
    start_urls = []

    def __init__(self, *a, **kw):
        super(WIPOjobSpider, self).__init__(*a, **kw)
        print("prepare to crawl WIPO")

    def start_requests(self):
        yield SplashRequest(url="https://wipo.taleo.net/careersection/wp_2/jobsearch.ftl?lang=en#",
                            callback=self.parselink,
                            args={'wait': 10})

    def parselink(self, response):
        job = scrapy.Selector(response)
        links = job.xpath('//div[@class="multiline-data-container"]/div/span/a/@href').extract()
        print("WIPO共" + str(len(links)) + "条网页待爬")
        for link in links:
            url = 'https://wipo.taleo.net' + link
            yield SplashRequest(url=url,
                                callback=self.parsejob,
                                args={'wait': 5})

    def parsejob(self, response):
        item = self.initItem()
        item["englishname"] = "WIPO"
        item["chinesename"] = "世界知识产权组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "瑞士"
        item["type"] = "知识产权"
        item["url"] = "http://www.wipo.int/portal/en/index.html"
        item["alljoburl"] = "https://wipo.taleo.net/careersection/wp_2/jobsearch.ftl?lang=en#"
        item["joburl"] = response.url
        response = scrapy.Selector(response)

        work = response.xpath('//div[@class="editablesection"]/div[1]').xpath('string(.)').extract()[0]
        item["work"] = re.sub('\W', '', work.split('-')[0])  # 岗位

        sector = response.xpath('//div[@class="editablesection"]/div[2]').xpath('string(.)').extract()[0]
        item["belong"] = sector  # 部门、组织机构

        grade = response.xpath('//div[@class="editablesection"]/div[3]').xpath('string(.)').extract()[0]
        item["PostLevel"] = re.sub('\W', '', grade.split('-')[1])  # 职级

        contract = response.xpath('//div[@class="editablesection"]/div[4]').xpath('string(.)').extract()[0]
        item["contracttime"] = re.sub('\W', '', contract.split('-')[-1])  # 合同期限

        DutyStation = response.xpath('//div[@class="editablesection"]/div[5]').xpath('string(.)').extract()[0]
        item["Location"] = re.sub('\W', '', DutyStation.split(':')[-1])  # 工作地点

        time = response.xpath('//div[@class="editablesection"]/div[6]').xpath('string(.)').extract()[0]  # 时间
        item["issuedate"] = re.sub('\W', '', time.split('Application Deadline')[0].split(':')[-1])  # 发布时间
        item["ApplicationDeadline"] = re.sub('\W', '', time.split('Application Deadline')[-1])  # 截止时间

        requireinfo = response.xpath('//div[@class="editablesection"]/div[7]')
        require = StrUtil.delMoreSpace(re.sub('\n', ' ', requireinfo.xpath('string(.)').extract()[0]))

        try:
            item["description"] = re.search(r"Organizational(.*)Duties and responsibilities", require, re.I).group(
                1)  # 组织背景
        except:
            pass

        try:
            item["responsibilities"] = re.search(r"Duties and responsibilities(.*)Requirements", require, re.I).group(
                1)  # 职能
        except:
            pass
        try:
            Requirements = re.search(r"Requirements(.*)Organizational competencies", require, re.I).group(1)  # 要求
            item["experience"] = re.search(r'Experience(.*)Languages', Requirements, re.I).group(1)
        except:
            pass

        try:
            item["education"] = re.search(r'Education(.*)Experience Ess', Requirements, re.I).group(1)  # 教育背景
        except:
            pass

        try:
            item["language"] = re.search(r'Languages(.*)Job-related', Requirements, re.I).group(1)  # 语言
        except:
            pass

        try:
            item["skill"] = re.search(r"Job-related(.*)Information", require, re.I).group(1)  # 技能
        except:
            pass

        try:
            item["addition"] = StrUtil.delMoreSpace(require.split('Organizational context')[-1].split
                                                    ('Duties and responsibilities')[-1].split('Requirements')[-1].split(
                'Organizational competencies')[-1].split('Information')[-1])  # 附加信息
        except:
            pass
        self.debugItem(item)
        self.insert(item)
