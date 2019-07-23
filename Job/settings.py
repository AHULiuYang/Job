# -*- coding: utf-8 -*-


BOT_NAME = 'Job'

SPIDER_MODULES = ['Job.spiders.jobSpider']
NEWSPIDER_MODULE = 'Job.spiders.jobSpider'

DOWNLOAD_DELAY = 0.1
DOWNLOAD_TIMEOUT = 100

DB = 'job'
MYSQLDB_CONNECT = {
    'user': 'root',
    'port': 3306,
    'passwd': 'root',
    'host': 'localhost',
    'charset': 'utf8',
    'use_unicode': False,
}

SPLASH_URL = 'http://192.168.99.100:8050'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
    'Job.middlewares.agentMiddleware.RotateUserAgentMiddleware' :400,
    # 'Job.middlewares.proxyMiddleware.proxyMiddleware': 544,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

ITEM_PIPELINES = {
    'Job.pipelines.pipeline.JobPipeline': 300,
}

LOG_LEVEL = 'DEBUG'
# HTTPCACHE_ENABLED = True
HTTPCACHE_IGNORE_HTTP_CODES = [301,302]
HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'cache'
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.DummyPolicy'
