# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AllJobs(scrapy.Item):
    englishname = scrapy.Field() #英文缩写
    chinesename = scrapy.Field() #中文名称
    incontinent = scrapy.Field() #所属洲
    incountry = scrapy.Field()   #所在地
    type = scrapy.Field()        #分类
    url = scrapy.Field()         #主页url
    alljoburl = scrapy.Field()   #招聘岗位网址
    joburl = scrapy.Field()      #职位url
    work = scrapy.Field()        #职位名
    issuedate = scrapy.Field()   #发布日期
    ApplicationDeadline = scrapy.Field() #截止时间
    description = scrapy.Field()    #职位介绍
    responsibilities = scrapy.Field()  #职能
    skill = scrapy.Field()        #技能
    PostLevel = scrapy.Field()   #职级
    belong = scrapy.Field()      #组织机构
    language = scrapy.Field()   #语言
    contracttime = scrapy.Field()   #初始合同时间
    Location = scrapy.Field()    #工作地点
    full_time = scrapy.Field()   #是否全职
    treatment = scrapy.Field()   #待遇
    education = scrapy.Field()   #教育背景
    addition = scrapy.Field()    #附加
    experience = scrapy.Field()  #工作经历