#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime

RULES = dict(
    l5=dict(a="%y", al=2, bl=3, c="normal"),
    l7=dict(a="%Y", al=4, bl=3, c="normal"),
    l8=dict(a="%y%m%d", al=6, bl=2, c="high"),
    l9=dict(a="%y%m%d", al=6, bl=3, c="high"),
    l10=dict(a="%Y%m%d", al=8, bl=2, c="high"),
    l11=dict(a="%Y%m%d", al=8, bl=3, c="high"),
)


def gcd(a, b):
    """
    计算最大公约数
    """
    if b == 0:
        return a
    return gcd(b, a % b)


def is_cron(date, cron):
    """
    determine whether it is the time match the value
    value format:
    minute houre day month week
    like:
    1 * * * *

    :returns: True or False

    """
    for value in cron:
        match = True
        sp = value.split()
        if len(sp) != 5:
            continue
        for item in zip(sp, ['minute', 'hour', 'day', 'month', 'week']):
            if not match_one_slot(date, *item):
                match = False
                break
        if not match:
            continue
        else:
            return True
    return False


def match_one_slot(now, value, slot_type):
    """
    called by is_cron
    determine one type of format
    value is a string like '*/5' or '2' or '*'
    slot_type is one of : minute houre day month week
    week: from 0 to 6, 0 is sunday
    """
    n = getattr(now, slot_type) if slot_type != 'week' else ((now.weekday()+1) % 7)
    for area in value.split(','):
        sp = area.split('/')
        mod = int(sp[1]) if len(sp) > 1 else 1
        mod_start = 0
        pattern = sp[0]
        sp = pattern.split('-')
        rng = []
        if '-' in pattern and len(sp) == 2:
            # case like: 0-59
            rng = range(int(sp[0]), int(sp[1])+1)
            mod_start = int(sp[0])
        if pattern in ['*', str(n)] or n in rng:
            # match patter, consider mod
            if (n - mod_start) % mod == 0:
                # all match
                return True
    return False


class Issue(object):
    """
    该class认为，期号的规律模型是a+b型，其中a可以为空，若不为空时，则是日期相关，b必不为空，且是逐一递加，但当a发生变动时，b会从1开始重新递加
    a的相关属性有
        a_valid (bool):是否有a
        a_format (string):类似于%Y%m%d这样的日期格式字符串
        a_freq (enum('day','month','year')):标识在什么级别的时间间隔下a会发生变动。该属性其实可以通过format推测得出
    b的相关属性有
        b_length (int):b的长度，一般应该为3，如果设置为0，则为长度不限。该属性可通过base_issue和base_date推测

    issue长度和a，b有一一对应关系（见RULES）因此可以只传入issue_length而不传入a，b。当有issue_length时，会无视ab参数

    其他属性
        open_cron (list):类似于["*/10 9-18 * * *", "*/5 18-21 * * *"]这样的的cron形式的字符串列表，用于描述开奖时段及周期
        category (enum('全国','地方','高频'))
    """

    # TODO: 计算/记录不开奖时段，如春节
    spring_fes = {
        "2013": "02-10",
        "2014": "01-30",
        "2015": "02-18",
        "2016": "02-07",
        "2017": "01-27",
        "2018": "02-15",
        "2019": "02-04",
        "2020": "01-24",
    }
    FREQ_ENUM = ('year', 'month', 'day')

    def __init__(self, issue_length=None, a_valid=True, a_format="%Y", category="", open_cron=[], b_length=3, a_freq=None):
        self.a_valid = a_valid
        self.a_format = a_format
        self.category = category
        self.open_cron = open_cron
        self.b_length = b_length
        # 优先使用issue_length
        if issue_length:
            r = RULES.get('l%s' % issue_length)
            if r:
                self.a_format = r['a']
                self.b_length = r['bl']
        if not a_freq:
            # 目前暂时只有year和day两种情况，所以做简单的逻辑判断，不考虑其他情况
            if "%d" in self.a_format:
                self.a_freq = 'day'
            else:
                self.a_freq = 'year'
        self.escape_range = []
        for year in self.spring_fes:
            start = datetime.datetime.strptime(year+'-'+self.spring_fes[year], '%Y-%m-%d')
            end = start + datetime.timedelta(days=7)
            self.escape_range.append((start, end))

    def __get_open_time(self, reverse=False):
        """
        根据self.open_cron计算最早/晚开奖时间（%H:%M格式）
        reverse False给出最早开奖时间  True给出最晚开奖时间
        """
        tmp_list=[]
        sort_func = max if reverse else min
        for cron in self.open_cron:
            # 从cron里找出开奖的最早时间（主要是针对高频，其他基本不需要特别处理，直接选取minute项和hour项）
            sp = cron.split()
            minute_sp = sp[0].replace('*', '0').split('/')[0].split(',')
            minute = sort_func([int(i.split('-')[0]) for i in minute_sp])
            hour_sp = sp[1].replace('*', '0').split('/')[0].split(',')
            hour = sort_func([int(i.split('-')[0]) for i in hour_sp])
            tmp_list.append((hour, minute))
        return sort_func(tmp_list)

    def __full_issue(self, open_date, b):
        """
        根据输入的b和a_valid&a_format，输出完整格式的issue
        """
        if self.a_valid:
            b = str(b)
            b = "0"*(self.b_length-len(b))+b
            return "%s%s" % (open_date.strftime(self.a_format),b)
        else:
            return str(b)

    def get_step(self):
        return self.__get_step()

    def __get_step(self):
        """
        根据open_cron计算日期迭代最小粒度，返回值为datetime.datetime.timedelta对象
        """
        tmp_list = [7*86400]
        delta_map = {0:60, 1:3600, 2:86400, -1:7*86400}
        for cron in self.open_cron:
            sp = cron.split()
            #根据实际情况，不考虑月级的delta，最大考虑到日级delta，故只需要考虑sp[0], sp[1], sp[2] sp[-1]
            for k in delta_map:
                if '/' in sp[k]:
                    delta = int(sp[k].split('/')[-1]) * delta_map[k]
                    tmp_list.append(delta)
                elif '*' == sp[k]:
                    delta = delta_map[k]
                    tmp_list.append(delta)
        if len(tmp_list) > 1:
            delta = reduce(gcd,tmp_list)
        else:
            delta = tmp_list[0]
        return datetime.timedelta(seconds=delta)

    def __get_max_issue(self, base_date):
        """
        计算base_date所在周期内最大期数信息
        """
        if not self.a_valid:
            return 0  #a_valid无效，说明无周期，从头计数到尾
        last_item = None
        for item in self.__get_a_frame_issue_list(base_date):
            if item['open_time'].strftime(self.a_format) != base_date.strftime(self.a_format):
                return last_item
            last_item = item


    def __issue_iter(self, base_date, b, step, reverse=False):
        """
        期号计算逻辑，根据传入的base_date、b、step进行期号的正向或反向迭代计算。
        base_date（datetime）, b（int）基准期号的日期及b部分（a部分通过a_valid和a_format计算，故不需要传入）
        reverse 迭代方向是否是反向递减
        max_b 如果是反向迭代，当b减到最小，需要继续往下减时，需要a部分-1，b部分设置为该周期最大值，所以需要知道a周期以内b最大会加到多少。如果此值为0，当迭代到b=0时，退出迭代
        #TODO: max_b的方案不靠谱，每年的期数不固定，所以无法确定max_b，考虑使用别的方案进行reverse
        """
        b_step = 1 if not reverse else -1
        last_date = now_date = base_date
        now_b = int(b) - b_step
        while True:
            if is_cron(now_date, self.open_cron):
                escape = False
                for rng in self.escape_range:
                    if now_date>rng[0] and now_date<rng[1]:
                        escape = True
                        break
                if not escape:
                    now_b += b_step
                    yield dict(
                        issue = self.__full_issue(now_date, now_b),
                        open_time = now_date,
                        )
            last_date = now_date
            if reverse:
                now_date -= step
            else:
                now_date += step
            if self.a_valid and (last_date.strftime(self.a_format) != now_date.strftime(self.a_format)): # a有效且a发生变化，b要重新计数
                if not reverse:
                    now_b = 1 - b_step
                else:
                    max_issue = self.__get_max_issue(now_date)
                    if not max_issue:
                        #可能出什么问题了，先当无数据扔回去
                        break
                    now_b = int(max_issue['issue'][-self.b_length:]) - b_step
                    last_date = now_date = max_issue['open_time']



    def __get_a_frame_issue_list(self, mark_date, reverse=False):
        """
        mark_date 基准时间, datetime格式
        基准时间开始，迭代输出mark_date所在a时间段内期号的的迭代器。若a无效，则直接返回None
        返回：
        迭代器每一个输出项为：
        {
            'issue': '2016053',
            'open_time': datetime,
            'concern_range': ('2016-05-01 21:25', '2016-05-03 21:25'),  #concern_range是指该期的关心时段。关心时段定义为：上期开奖时间n秒后到本期开奖时间n秒后
        }
        """
        if not self.a_valid:
            return
        param = dict(year=1, month=1, day=1) if not reverse else dict(year=2099, month=12, day=31)
        for dim in self.FREQ_ENUM:
            param[dim] = getattr(mark_date, dim)
            if dim == self.a_freq: break
        hour, minute = self.__get_open_time(reverse)
        param.update(dict(
                        minute=minute,
                        hour=hour
                        ))
        count_start = datetime.datetime(**param)
        delta = self.__get_step()
        if reverse:
            start_b = int(self.__get_max_issue(count_start)['issue'][-self.b_length:])
        else:
            start_b = 1
        for item in self.__issue_iter(count_start, start_b, delta, reverse=reverse):
            yield item

    def __date_format(self, date):
        if type(date) == type(''):
            df = '%Y-%m-%d' if date.find(':')<0 else '%Y-%m-%d %H:%M'
            return datetime.datetime.strptime(date, df)
        else:
            return date

    def get_issue_list(self, start_date=None, reverse=False):
        """
        从start_date开始，正(逆)向迭代输出期号。
        start_date如果为None，则默认为当前时刻
        start_date可接受数据格式为datetime对象或yyyy-mm-dd 或 yyyy-mm-dd hh:mm 字符串格式
        """
        start_date = self.__date_format(start_date) if start_date else datetime.datetime.now()
        for item in self.__get_a_frame_issue_list(start_date, reverse):
            if reverse and start_date>= item['open_time'] or not reverse and start_date<=item['open_time']:
                yield item

    def get_recent_issues(self, before, after):
        """
        返回近期期号，并标记[当期]位置
        以x-1期开奖n秒后到x期开奖n秒后为时间段划分每一期的区间，当前时间所落在的区间为关心时段，该区间内的期为当期
        n值根据彩种而有区别。全国、地方彩种 n=20*60秒，高频彩种 n=3*60秒
        返回 近期列表，当期信息 列表以时间从早到晚正序排列
        """
        now = datetime.datetime.now()
        #now = datetime.datetime(2016,6,2,21,16,0)
        mark_date = now.strftime("%Y-%m-%d")
        before_list = []
        after_list = []
        before_iter = self.get_issue_list(mark_date, reverse=True)
        i = before
        while i>=0:
            before_list.append(before_iter.next())
            i -= 1
        before_list.reverse()
        i = after
        after_iter = self.get_issue_list(mark_date, reverse=False)
        while i>=0:
            after_list.append(after_iter.next())
            i -= 1
        n = 3*60 if self.category == '高频' else 20*60
        now_issue = None
        total_list = before_list+after_list
        last = total_list[0]
        for issue in total_list[1:]:
            if (now - last['open_time']).total_seconds() > n > (now - issue['open_time']).total_seconds():
                now_issue = issue
                break
            last = issue
        now_issue = now_issue or last
        idx = total_list.index(now_issue)
        return total_list[idx-before:idx+after+1], now_issue

# Issue Class End


def format_issue(issue, length):
    """输入issue和想要转换的长度，该函数尝试对其进行转换以符合length要求。如果发现有问题，返回None，没问题返回转换后的issue"""
    now_rule = RULES.get("l%s"%len(issue))
    if not now_rule:
        return None
    target_rule = RULES.get("l%s"%length)
    if not target_rule:
        return None
    if now_rule['c'] != target_rule['c']:
        logging.info("category unmatch, can not change between normal and high freq")
        return None
    now = datetime.datetime.now()
    try:
        a = issue[:now_rule["al"]]
        b = int(issue[now_rule["al"]:])
        if len(a) in (6,8):
            day = int(a[-2:])
            month = int(a[-4:-2])
            year = int(a[:-4])
        else:
            year = int(a)
            month = now.month
            day = now.day
    except:
        # 不可识别的期号
        import traceback
        print traceback.format_exc()
        return None

    # 期号日期规则检查，日期不可大于当前日期
    _year = year if year > 2000 else 2000+year
    issue_date = "%04d%02d%02d" % (_year, month, day)
    if issue_date > now.strftime("%Y%m%d"):
        return None

    # 检查完毕，开始转换
    a = a[-target_rule["al"]:]
    if target_rule['al'] - len(a) == 2:
        a = "20" + a
    elif target_rule['al'] != len(a):
        # 理论上不应该到这儿
        logging.info("unexpected a: %s. args: %s, %s" % (a, issue, length))
        return None  # a部分有问题
    b = ("000%s" % b)[-target_rule["bl"]:]

    return a+b


class numunit(object):
    def __init__(self, value, miss=0, up=""):
        self.v = value
        self.m = miss
        self.u = up
    def miss(self):
        '''本期未出，遗漏+1，返回一个新的obj'''
        return numunit(self.v, self.m+1, "")
    def hit(self, up=""):
        '''本期出了，遗漏清0，up值根据命中数修改，返回一个新的obj'''
        return numunit(self.v, 0, up)
    def out_put(self):
        '''以tuple形式输出该单元格的值'''
        return [str(self.m), "0"] if self.m else [str(self.v), str(self.u)]
    def __str__(self):
        if self.m:
            return "%smiss_%s" % (self.v, self.m)
        else:
            return "%shit__%s" % (self.v, self.u)

def numunit_formater(obj):
    if isinstance(obj, numunit):
        return obj.out_put()

def numunit_miss_formater(obj):
    if isinstance(obj, numunit):
        return obj.m

def numunit_num_miss_formater(obj):
    if isinstance(obj, numunit):
        return {'name':obj.v, 'miss':obj.m}

def miss_calc(results, numrange):
    '''
    遗漏计算
    输入：results：结果数据dict列表，dict必要字段：issue和result，要求此列表输入排序为正序。numrange，取值范围，逗号分割
    输出：{'issue':str, 'result':str, 'miss':[numunit]} 的列表
    '''
    numrange = numrange.split(',')
    # 默认之前一期是全部命中
    _last = [numunit(n) for n in numrange]
    tmp = []
    for r in results:
        nums = dict()
        # 计算每个值都有几个（右上角标）
        for item in r['result'].split(','):
            nums[item] = nums.get(item,0)+1
        r['miss'] = []
        for i, n in enumerate(numrange):
            r['miss'].append(_last[i].miss() if not n in nums else _last[i].hit(up=nums[n]) )
        _last = r['miss']
        tmp.append(r)
    return tmp


if __name__ == '__main__':
    i = Issue(open_cron=["*/40 * * * *"], a_format="%y%m%d")
    for x in i.get_issue_list():
        print x
    data = [
        dict(issue="16001", result="2,4,6"),
        dict(issue="16002", result="1,5,8"),
        dict(issue="16003", result="2,3,3"),
        dict(issue="16004", result="0,3,5"),
        dict(issue="16005", result="1,2,3"),
    ]
    for item in miss_calc(data, '0,1,2,3,4,5,6,7,8,9'):
        print "\t".join(str(x.out_put()) for x in item['miss'])
    #print format_issue("160809023",11)
