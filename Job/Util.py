import re, os


class TimeUtil(object):
    month = {"january": "1", "jan": "1", "february": "2", "feb": "2", "march": "3", "mar": "3", "april": "4",
             "apr": "4", "may": "5", "june": "6", "jun": "6", "july": "7", "jul": "7", "august": "8", "aug": "8",
             "september": "9", "seq": "9", "october": "10", "oct": "10", "november": "11", "nov": "11",
             "december": "12", "dec": "12"}


class StrUtil(object):
    def __init__(self):
        print("StrUtil ok")
        '''字符串处理工具'''

    @staticmethod
    def delWhiteSpace(msg):
        pattern = re.compile('\\s+')
        return (re.sub(pattern, ' ', msg)).strip()

    @staticmethod
    def delMoreSpace(msg):
        return ' '.join(msg.split())

    @staticmethod
    def delWhite(msg):
        pattern = re.compile('\\s+')
        return (re.sub(pattern, '', msg)).strip()


def judge_is_null(content):
    if len(content):
        return content[0]
    else:
        return ""


def retain_letter(content):
    return re.sub("[^A-Za-z]", "", content)
