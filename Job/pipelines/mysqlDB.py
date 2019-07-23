class myaqlSave(object):

    def insertjobs(self, tx, conn, item):
        content = 'insert into 岗位(英文缩写,中文名称,岗位url,岗位名称,工作地点,职级,发布日期,截止日期,职位介绍,职能,技能,组织机构,语言,初始合同时间,是否全职,待遇,教育背景,附加的,工作经历)'
        content_ = 'insert into 2019_7_20(英文缩写,中文名称,岗位url,岗位名称,工作地点,职级,发布日期,截止日期,职位介绍,职能,技能,组织机构,语言,初始合同时间,是否全职,待遇,教育背景,附加的,工作经历)'
        type = 'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            tx.execute(content + type, (
                item["englishname"], item["chinesename"], item['joburl'], item['work'], item['Location'],
                item['PostLevel'], item['issuedate'], item['ApplicationDeadline'], item['description'],
                item['responsibilities'], item['skill'], item['belong'], item['language'], item['contracttime'],
                item['full_time'], item['treatment'], item['education'], item['addition'], item['experience'])
                       )
            conn.commit()

            tx.execute(content_ + type, (
                item["englishname"], item["chinesename"], item['joburl'], item['work'], item['Location'],
                item['PostLevel'], item['issuedate'], item['ApplicationDeadline'], item['description'],
                item['responsibilities'], item['skill'], item['belong'], item['language'], item['contracttime'],
                item['full_time'], item['treatment'], item['education'], item['addition'], item['experience'])
                       )
            conn.commit()

        except Exception as e:
            print("存储岗位数据失败" + str(e))
