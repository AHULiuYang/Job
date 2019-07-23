import scrapy
import re
from scrapy.http import Request
from scrapy_splash import SplashRequest
from Job.spiders.baseSpider import baseSpider
from Job.Util import *


class UNDPjobSpider(baseSpider):
    name = "UNDPjob"
    start_urls = ["https://jobs.undp.org/cj_view_jobs.cfm"]

    def __init__(self, *a, **kw):
        super(UNDPjobSpider, self).__init__(*a, **kw)
        self.preurl = "https://jobs.undp.org/"

    def parse(self, response):
        selector = scrapy.Selector(response)
        print("prepare to crawl UNDP")
        table = selector.xpath('//div[@id="content-main"]/table[@class="table-sortable"]')
        for evertable in table:
            for everlink in evertable.xpath('tr')[:-1]:
                link = judge_is_null(everlink.xpath('td[1]/a/@href').extract())
                if link == "": continue
                if link.startswith("c"):
                    link = self.preurl + link
                describe = judge_is_null(everlink.xpath('td[1]/a/text()').extract())
                suoshu = judge_is_null(everlink.xpath('td[2]/text()').extract())
                work = self.tostring(judge_is_null(everlink.xpath('td[3]/text()').extract()))
                applytime = judge_is_null(everlink.xpath('td[4]/text()').extract())
                if link.endswith('id=2'):
                    print("start to crawl [%s] by splash" % link)
                    yield SplashRequest(url=link,
                                        callback=self.crawl_iframe,
                                        meta={"describe": describe, "suoshu": suoshu, "applytime": applytime},
                                        args={'wait': 2})
                else:

                    print("start to crawl [%s] by request" % link)
                    yield Request(url=link,
                                  callback=self.UNDP_prase,
                                  meta={"describe": describe, "suoshu": suoshu, "work": work, "applytime": applytime})

    def UNDP_prase(self, response):
        job = scrapy.Selector(response)
        item = self.initItem()
        item["joburl"] = response.url
        item["PostLevel"] = response.meta["work"]
        item["work"] = response.meta["describe"]
        item["belong"] = response.meta["suoshu"]
        item["issuedate"] = ""
        item['incontinent'] = '北美洲'
        item['alljoburl'] = 'https://jobs.undp.org/cj_view_jobs.cfm'
        item['type'] = '科学研究'
        item['englishname'] = 'UNDP'
        item['chinesename'] = '联合国开发计划署'
        item['url'] = 'http://www.undp.org/'
        item['incountry'] = '美国'
        self.crawl_noid(job, item)
        # self.debugItem(item)
        self.insert(item)

    def crawl_noid(self, job, item):
        base_key_names = ["Location", "ApplicationDeadline", "LanguagesRequired", "DurationofInitialContract"]
        add_key_names = {'Background': 'description',
                         'DutiesandResponsibilities': 'responsibilities',
                         'Competencies': 'skill'}
        trs = job.xpath('//div[@id="content-main"]/table[1]/tr')
        for tr in trs:
            if len(tr.xpath("td")) == 1: continue
            key_name = retain_letter(judge_is_null(tr.xpath('td[1]/strong/text()').extract()))
            context = judge_is_null(tr.xpath('td[2]/text()').extract())
            if key_name not in base_key_names:
                continue
            if key_name == "LanguagesRequired":
                item["language"] = self.tostring(context)
            elif key_name == "DurationofInitialContract":
                item["contracttime"] = self.tostring(context)
            else:
                item[key_name] = self.tostring(context)
        trs = job.xpath('//div[@id="content-main"]/table[2]/tr')
        for i in range(0, len(trs) - 1, 1):
            key_name = retain_letter(judge_is_null(trs[i].xpath('td[@class="field"]/h5/text()').extract()))
            info = judge_is_null(trs[i + 1].xpath('td[@class="text"]').xpath('string(.)').extract())
            if key_name in add_key_names.keys():
                item[add_key_names[key_name]] = self.tostring(info)
            elif "Skills" in key_name:
                try:
                    item['education'] = self.tostring(re.search(r'Education(.*?)Exp[e,é]rience:', info, re.I).group(1))
                    item['experience'] = self.tostring(re.search(r'Exp[eé]rience(.*?)Langu', info, re.I).group(1))
                except:
                    item['education'] = self.tostring(info)
                    item['experience'] = self.tostring(info)

    def crawl_iframe(self, response):
        selector = scrapy.Selector(response)
        link = selector.xpath('//iframe/@src').extract()[0]
        yield Request(url=link, callback=self.crawlhaveid, meta=response.meta, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Cookie": "ExpirePage=https://jobs.partneragencies.net/psc/UNDPP1HRE2/; PS_LOGINLIST=https://jobs.partneragencies.net/UNDPP1HRE2; p1hre2-8250-PORTAL-PSJSESSIONID=TMB5ZmwQvtQrGcvRttShnVM28z3TdJv6!-454263630; PS_TOKEN=AAAAvAECAwQAAQAAAAACvAAAAAAAAAAsAARTaGRyAgBOiQgAOAAuADEAMBQyejPz3FSX5ezsObx1koeyEUlRZAAAAHwABVNkYXRhcHicLcpBCoJQEMbx/1Nx2TncKC97oB2gdBWS7kXKhRAikeAVulOH81MamN/MfAzwNZ4fYFB5v82Inrf6IWcGPiS6Fs0tH+l4KXkyhVy4URyoqLnS0FJyd6RYjmTE0u7m/z2RJ2lx0inP988zKxWUEdw=; SignOnDefault=erecruit.external.dp; ACE-JOBS=R4226155932; PS_TOKENEXPIRE=18_Oct_2017_06:27:34_GMT",
            "Host": "jobs.partneragencies.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        })

    def crawlhaveid(self, response):
        item = self.initItem()
        item['joburl'] = response.url
        item["description"] = response.meta["describe"]
        item["belong"] = response.meta["suoshu"]
        item["issuedate"] = ""
        item['incontinent'] = '北美洲'
        item['alljoburl'] = 'https://jobs.undp.org/cj_view_jobs.cfm'
        item['type'] = '科学研究'
        item['englishname'] = 'UNDP'
        item['chinesename'] = '联合国开发计划署'
        item['url'] = 'http://www.undp.org/'
        item['incountry'] = '美国'
        field = ['Agency', 'Title', 'Job ID', 'Practice Area - Job Family', 'Vacancy End Date', 'Time Left',
                 'Duty Station', 'Education & Work Experience', 'Languages', 'Grade', 'Vacancy Type',
                 'Posting Type',
                 'Bureau', 'Contract Duration', 'Background', 'Duties and Responsibilities', 'Competencies',
                 'Required Skills and Experience',
                 'Disclaimer']
        id2field = {'Agency': '',
                    'Title': 'work',
                    'JobID': '',
                    'PracticeAreaJobFamily': 'belong',
                    'VacancyEndDate': 'ApplicationDeadline',
                    'DutyStation': 'Location',
                    'TimeLeft': '',
                    'EducationWorkExperience': 'education',
                    'Languages': 'language',
                    'Grade': 'PostLevel',
                    'VacancyType': '',
                    'PostingType': '',
                    'Bureau': '',
                    'ContractDuration': 'contracttime',
                    'Background': 'description',
                    'DutiesandResponsibilities': 'responsibilities',
                    'Competencies': 'skill',
                    'RequiredSkillsandExperience': 'experience',
                    'Disclaimer': 'addition'}

        selector = scrapy.Selector(response)
        table = selector.xpath("//table[@id='ACE_$ICField30$0']/tr/td")
        tds = [t.strip() for t in table.xpath("string(.)").extract()]
        table2 = selector.xpath("//table[@id='ACE_HRS_JO_PST_DSCR$0']/tr/td")
        tds2 = [t.strip() for t in table2.xpath("string(.)").extract()]
        tds.extend(tds2)
        tds.append('Disclaimer')
        temp = []
        key = 'default'
        value = ''
        try:
            for td in tds:
                if td in field:
                    value = ''.join(temp)
                    try:
                        if key not in ['JobID', 'TimeLeft', 'VacancyType', 'PostingType', 'Bureau', 'Agency']:
                            item[id2field.get(key)] = self.tostring(value)
                    except:
                        pass
                    temp = []
                    key = re.sub('[-& ]', '', td)
                else:
                    temp.append(td)
        except:
            print('parser error!')
        self.debugItem(item)
        self.insert(item)
