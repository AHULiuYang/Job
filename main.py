import warnings

warnings.filterwarnings("ignore")
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from Job.spiders.jobSpider.crawlUNDPjobs import UNDPjobSpider
from Job.spiders.jobSpider.crawlCERNjobs import CERNjobsSpider
from Job.spiders.jobSpider.crawlITERjobs import ITERJobSpider
from Job.spiders.jobSpider.crawlUNEPjobs import UNEPJobSpider
from Job.spiders.jobSpider.crawlOECDjobs import OECDJobSpider
from Job.spiders.jobSpider.crawlUNIDOjobs import UNIDOjobLink
from Job.spiders.jobSpider.crawlUNUjobs import UNUjobSpider
from Job.spiders.jobSpider.crawlWHOjobs import WHOjobSpider
from Job.spiders.jobSpider.crawlWIPOjobs import WIPOjobSpider
from Job.spiders.jobSpider.crawlESCAPjobs import ESCAPjobsSpider
from Job.spiders.jobSpider.crawlUNESCOjobs import UNESCOjobSpider

import scrapydo
scrapydo.setup()



def start():
    spiders = [
        UNDPjobSpider,
        # ESCAPjobsSpider,
        # UNESCOjobSpider,
        # ITERJobSpider,
        # CERNjobsSpider,
        #
        # UNIDOjobLink,
        # UNUjobSpider,
        # WHOjobSpider,
        # UNEPJobSpider,
        # OECDJobSpider,
        # WIPOjobSpider
    ]

    for spider in spiders:
        scrapydo.run_spider(spider_cls=spider)
start()

