import scrapy
import json
import requests
from scrapy_splash import SplashRequest
from ..baseSpider import baseSpider
from fake_useragent import UserAgent
from Job.Util import *

ua = UserAgent()
month = TimeUtil().month


def format_date(date):
    date = date.split(",")[:2]
    date = "/".join([date[0].split()[1], month[date[0].split()[0].lower()], date[1].strip()])
    return date


class WHOjobSpider(baseSpider):
    name = "WHOjob"

    def __init__(self, *a, **kw):
        super(WHOjobSpider, self).__init__(*a, **kw)
        print("prepare to crawl WHO")
        self.preurl = "https://careers.who.int/careersection/ex/jobdetail.ftl?job="

    def start_requests(self):
        ur = "https://careers.who.int/careersection/rest/jobboard/searchjobs?lang=en&portal=101430233"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Content-Length": "948",
            "Content-Type": "application/json",
            "Cookie": "locale=en; _ga=GA1.2.1191498199.1561537238; _gid=GA1.2.972556960.1561537238; __atuvc=1%7C26; __atu",
            "Host": "careers.who.int",
            "Origin": "https://careers.who.int",
            "Referer": "https://careers.who.int/careersection/ex/jobsearch.ftl",
            "tz": "GMT+08:00",
            "User-Agent": ua.random,
            "X-Requested-With": "XMLHttpRequest"
        }
        data = json.loads(
            '{"multilineEnabled":true,"sortingSelection":{"sortBySelectionParam":"3","ascendingSortingOrder":"false"},"fieldData":{"fields":{"KEYWORD":"","LOCATION":""},"valid":true},"filterSelectionParam":{"searchFilterSelections":[{"id":"POSTING_DATE","selectedValues":[]},{"id":"LOCATION","selectedValues":[]},{"id":"JOB_FIELD","selectedValues":[]},{"id":"JOB_TYPE","selectedValues":[]},{"id":"JOB_SCHEDULE","selectedValues":[]},{"id":"JOB_LEVEL","selectedValues":[]},{"id":"EMPLOYEE_STATUS","selectedValues":[]}]},"advancedSearchFiltersSelectionParam":{"searchFilterSelections":[{"id":"ORGANIZATION","selectedValues":[]},{"id":"LOCATION","selectedValues":[]},{"id":"JOB_FIELD","selectedValues":[]},{"id":"JOB_NUMBER","selectedValues":[]},{"id":"URGENT_JOB","selectedValues":[]},{"id":"EMPLOYEE_STATUS","selectedValues":[]},{"id":"JOB_SCHEDULE","selectedValues":[]},{"id":"JOB_TYPE","selectedValues":[]},{"id":"JOB_LEVEL","selectedValues":[]}]},"pageNo":"3"}')

        for i in range(1, 6, 1):
            data["pageNo"] = i
            post_data = json.dumps(data)
            response = requests.post(ur, data=post_data, headers=headers)
            result = json.loads(response.text)
            for everydata in result["requisitionList"]:
                work = everydata["column"][0]
                num = everydata["column"][1]
                Location = everydata["column"][2].strip('[').strip(']').strip('"')
                PostLevel = everydata["column"][3]
                ContractualArrangement = everydata["column"][4]
                ClosingDate = format_date(everydata["column"][5])
                print("prepore to crawl %s" % self.preurl + num)
                yield SplashRequest(url=self.preurl + num,
                                    callback=self.parseWHOjob,
                                    meta={'work': work,
                                          'Location': Location,
                                          'PostLevel': PostLevel,
                                          'ContractualArrangement': ContractualArrangement,
                                          'ClosingDate': ClosingDate},
                                    args={'wait': 2})

    def parseWHOjob(self, response):
        item = self.initItem()
        item["englishname"] = "WHO"
        item["chinesename"] = "世界卫生组织"
        item["incontinent"] = "欧洲"
        item["incountry"] = "瑞士"
        item["type"] = "卫生"
        item["url"] = "http://www.who.int/en/"
        item["alljoburl"] = "https://tl-ex.vcdp.who.int/careersection/ex/jobsearch.ftl#"
        item["joburl"] = response.url
        item["work"] = response.meta["work"]
        item["Location"] = response.meta["Location"]
        item["PostLevel"] = response.meta["PostLevel"]
        item['ApplicationDeadline'] = response.meta["ClosingDate"]
        sel = scrapy.Selector(response).xpath('//div[@class="editablesection"]')
        num_span = 'div/span[@id="requisitionDescriptionInterface.%s.row1"]/text()'
        item["contracttime"] = judge_is_null(sel.xpath(num_span % ("ID" + str(1522))).extract())
        item["issuedate"] = format_date(judge_is_null(sel.xpath(num_span % "reqPostingDate").extract()))
        item["belong"] = judge_is_null(sel.xpath(num_span % ("ID" + str(1792))).extract())
        item["full_time"] = judge_is_null(sel.xpath(num_span % ("ID" + str(1842))).extract())
        for id in ["1894", "1882"]:
            data_xpath = 'div/span[@id="requisitionDescriptionInterface.ID%s.row1"]' % id
            data = self.tostring(judge_is_null(sel.xpath(data_xpath).xpath('string(.)').extract()))
            if data != "":
                break
        if 'DESCRIPTION OF DUTIES' in data:
            info = data.split('DESCRIPTION OF DUTIES')
            item['description'] = info[0]
        elif 'Summary of Assigned Duties:' in data:
            info = data.split('Summary of Assigned Duties:')
            item['description'] = info[0]
        else:
            info = data
        if 'REQUIRED QUALIFICATIONS' in info[-1]:
            info2 = info[-1].split('REQUIRED QUALIFICATIONS')
            item['responsibilities'] = info2[0]
        elif 'Recruitment Profile Competencies:' in info[-1]:
            info2 = info[-1].split('Recruitment Profile Competencies:')
            item['responsibilities'] = info2[0]
        else:
            info2 = info
        if 'Education Essential:' in info2[-1]:
            info3 = info2[-1].split('Education Essential:')
        elif 'Education:' in info2[-1]:
            info3 = info2[-1].split('Education:')
        elif 'Education Qualifications' in info2[-1]:
            info3 = info2[-1].split('Education Qualifications')
            item['skill'] = info3[0]
        else:
            info3 = info2
        if 'Experience Essential:' in info3[-1]:
            info4 = info3[-1].split('Experience Essential:')
            item['education'] = info4[0]
        elif 'Experience:' in info3[-1]:
            info4 = info3[-1].split('Experience:')
            item['education'] = info4[0]
        else:
            info4 = info3
        if 'Skills' in info4[-1]:
            info5 = info4[-1].split('Skills')
            down = ''
            for text in info5[1:]:
                down += text
            info5[1] = down
            count = len(info5[2:])
            while count:
                info5.pop()
                count -= 1
            item['experience'] = info5[0]
        elif 'SKILLS:' in info4[-1]:
            info5 = info4[-1].split('SKILLS:')
            item['experience'] = info5[0]
        else:
            info5 = info4
        if 'Language' in info5[-1]:
            info6 = info5[-1].split('Use of Language Skills')
            item['skill'] = info6[0]
        else:
            info6 = info5
        if 'REMUNERATION' in info6[-1]:
            info7 = info6[-1].split('REMUNERATION')
            item['language'] = info7[0]
        elif 'Other Skills(e.g.IT)' in info6[-1]:
            info7 = info6[-1].split('Other Skills(e.g.IT)')
            item['addition'] = info7[-1]
        else:
            info7 = info6
        if 'ADDITIONAL INFORMATION' in info7[-1]:
            info8 = info7[-1].split('ADDITIONAL INFORMATION')
            item['treatment'] = info8[0]
            item['addition'] = info8[-1]
        self.debugItem(item)
        self.insert(item)
