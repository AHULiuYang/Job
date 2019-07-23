import pymysql
from Job import settings
from Job.pipelines.mysqlDB import myaqlSave


class JobPipeline(object):

    def __init__(self):
        self.myaqlsave = myaqlSave()
        self.conn = pymysql.connect(**settings.MYSQLDB_CONNECT)
        self.cursor = self.conn.cursor()
        try:
            self.conn.select_db(settings.DB)
        except:
            self.create_database(settings.DB)
            self.conn.select_db(settings.DB)
            self.init()

    def init(self):
        jobCommand = ('DROP TABLE IF EXISTS `岗位`;'
                    'CREATE TABLE `岗位` ('
                      '`英文缩写` varchar(20) DEFAULT NULL,'
                      '`中文名称` varchar(80) DEFAULT NULL,'
                      '`岗位url` varchar(150) NOT NULL,'
                      '`岗位名称` varchar(300) NOT NULL,'
                      '`工作地点` varchar(300) DEFAULT NULL,'
                      '`职级` varchar(50) DEFAULT NULL,'
                      '`发布日期` varchar(150) DEFAULT NULL,'
                      '`截止日期` varchar(150) DEFAULT NULL,'
                      '`职位介绍` text,'
                      '`职能` text,'
                      '`技能` text,'
                      '`组织机构` text,'
                      '`语言` text,'
                      '`初始合同时间` text,'
                      '`是否全职` varchar(50) DEFAULT NULL,'
                      '`待遇` text,'
                      '`教育背景` text,'
                      '`附加的` text,'
                      '`工作经历` text,'
                      'PRIMARY KEY (`岗位名称`(100),`岗位url`(100))'
                    ') ENGINE=InnoDB DEFAULT CHARSET=utf8;')

        orgCommand = ('DROP TABLE IF EXISTS `组织`;'
                        'CREATE TABLE `组织` ('
                          '`英文缩写` varchar(20) NOT NULL DEFAULT "",'
                          '`中文名称` varchar(80) DEFAULT "",'
                          '`所属洲` varchar(40) DEFAULT "",'
                          '`所在地` varchar(100) DEFAULT "",'
                          '`分类` varchar(40) DEFAULT "",'
                          '`主页url` varchar(80) DEFAULT "",'
                          '`招聘网址url` varchar(100) DEFAULT "",'
                          'PRIMARY KEY (`英文缩写`)'
                        ') ENGINE=InnoDB DEFAULT CHARSET=utf8;')

        leaderCommand = ('DROP TABLE IF EXISTS `allleader`;'
                            'CREATE TABLE `allleader` ('
                              '`姓名` varchar(50) NOT NULL DEFAULT "",'
                              '`职位` varchar(100) DEFAULT "",'
                              '`链接` varchar(255) NOT NULL DEFAULT "",'
                              '`机构` varchar(50) DEFAULT "",'
                              '`简历` text,'
                              '`部门` varchar(255) DEFAULT "",'
                              'PRIMARY KEY (`姓名`,`链接`)'
                            ') ENGINE=InnoDB DEFAULT CHARSET=utf8;')

        self.create_table(jobCommand,orgCommand,leaderCommand)

    def create_database(self, database_name):
        try:
            command = 'CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET \'utf8\' ' % database_name
            self.cursor.execute(command)
        except Exception as e:
            print('创建数据库异常:%s' % str(e))

    def create_table(self, *args):
        for _ in args:
            try:
                self.cursor.execute(_)
                self.conn.commit()
            except Exception as e:
                print('创建表异常:%s' % str(e))

    def process_item(self,item):
        self.myaqlsave.insertjobs(self.cursor, self.conn, item)

