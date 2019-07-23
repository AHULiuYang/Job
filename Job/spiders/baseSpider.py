from Job.allitems.jobitems import AllJobs
from scrapy.spiders import Spider
from Job.Util import StrUtil
from Job.pipelines.pipeline import JobPipeline


class baseSpider(Spider):

    name = 'baseSpider'

    def __init__(self, *a, **kw):
        super(baseSpider, self).__init__(*a, **kw)
        self.jobPipeline = JobPipeline()

    def initItem(self):
        '''
        初始化全部字段
        '''
        return {k:'' for k in AllJobs().fields}

    def debugItem(self,item):
        '''
       调试输出item
        '''
        for k,v in item.items():
            print('%s>>>%s'%(k,v))

    def insert(self,item):
        '''
        存储爬取得数据
        '''
        self.jobPipeline.process_item(item=item)

    def tostring(self,msg):
        '''
        将网页中的文本数据转换为空格分隔得字符串格式
        '''
        return StrUtil.delMoreSpace(StrUtil.delWhiteSpace(msg))



