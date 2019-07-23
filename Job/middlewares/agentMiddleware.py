from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from fake_useragent import UserAgent

ua_gen = UserAgent()


class RotateUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = ua_gen.random
        if ua:
            request.headers.setdefault('User-Agent', ua)
