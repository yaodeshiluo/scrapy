# coding: utf-8
import json
import re
from scrapy.utils.url import urljoin_rfc
import os


json_location = os.path.abspath(__file__) + r'/spiders/linux.json'
print json_location
def get_crawl_list(category):
    alist=[]
    with open(json_location, 'r') as f:
        query = json.load(f)
        if category is None:
            alist = query

        elif '&&' in category:
            caizhong = category.split('&&',1)[0]
            website = category.split('&&',1)[1]
            for i in query:
                print i.get('caizhong') == caizhong
                print i.get('website') == website
                if i.get('caizhong') == caizhong and i.get('website') == website:
                    print i.get('caizhong') == caizhong
                    alist.append(i)
        else:
            for i in query:
                if i.get('caizhong') == category:
                    alist.append(i)

    return alist

def get_url_list(response):
    url_list_raw = response.selector.xpath(response.meta.get('urllist'))

    special_urls = {'http://kjh.cailele.com/kj_ssq.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=100&term=%s',
                      'http://www.lecai.com/lottery/draw/list/52':'http://www.lecai.com/lottery/draw/ajax_get_detail.php?lottery_type=52&phase=%s',
                      'http://www.lecai.com/lottery/draw/view/1':'http://www.lecai.com/lottery/draw/ajax_get_detail.php?lottery_type=1&phase=%s',
                      'http://kjh.cailele.com/kj_3d.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=102&term=%s',
                      'http://kjh.cailele.com/kj_dlt.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=1&term=%s',
                      'http://caipiao.163.com/award/3d/':'http://caipiao.163.com/award/3d/%s.html',
                      'http://caipiao.163.com/award/qlc/':'http://caipiao.163.com/award/qlc/%s.html',
                      'http://caipiao.163.com/award/dlt/':'http://caipiao.163.com/award/dlt/%s.html',
                      'http://caipiao.163.com/award/ssq/':'http://caipiao.163.com/award/ssq/%s.html',
                      'http://www.zhcw.com/kaijiang/zhcw_qlc_index.html':'http://kaijiang.zhcw.com/zhcw/html/qlc/detail_%s.html',
                      'http://kjh.cailele.com/kj_qlc.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=101&&term=%s',
                      'http://www.lecai.com/lottery/draw/view/3':'http://www.lecai.com/lottery/draw/view/3/%s?',
                      'http://kjh.cailele.com/kj_p3.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=3&term=%s'}

    if special_urls.get(response.url):
        baseurl = special_urls.get(response.url)
        alist = []
        # latest_num = url_list_raw.xpath('text()').extract()[0]
        for i in url_list_raw.extract():
            url = baseurl%(i)
            alist.append(url)
            print alist
        return alist
    if response.meta.get('baseurl'):
        baseurl = response.meta.get('baseurl')
        alist = []
        for i in url_list_raw.extract():
            url = baseurl % (i)
            alist.append(url)
            print alist
        return alist

    # print 'no handle'
    print 'url_list is',url_list_raw.extract()
    url_list = []
    for url in url_list_raw.extract():
        full_url = response.urljoin(url)
        url_list.append(full_url)
    # print 'url_list is',url_list
    return url_list

def get_detail_list(sel,response):
    #只有response.meta里有detail这一项才会调用该函数
    tr_list = []
    '''最常见的xpath得到列表。相应的meta里的信息有useless_rows(!!!(tr_0)),得到tr_list'''
    if isinstance(response.meta.get('detail'),basestring):
        useless_rows = response.meta.get('useless_rows') if response.meta.get('useless_rows') else []
        append = None
        for tr_num, tr in enumerate(sel.xpath(response.meta.get('detail') + '//tr')):
            if tr_num in useless_rows:
                pass
            else:
                each_tr = []
                if append:
                    each_tr.append(append)
                    append = None
                for td_num,each_td in enumerate(tr.xpath('*')):
                    if each_td.xpath('@colspan'):
                        for i in range(int(each_td.xpath('@colspan').extract()[0])):
                            each_tr.append(each_td.xpath('string(.)').extract()[0])
                    else:
                        each_tr.append(each_td.xpath('string(.)').extract()[0])
                    if each_td.xpath('@rowspan'):
                        append = each_td.xpath('string(.)').extract()[0]

                tr_list.append(each_tr)
        '''
        detail 为list有两种情况，即是否有other_response，以下是无的处理。
        '''
        #无other_response,或其为空
    elif isinstance(response.meta.get('detail'), list) \
            and not response.meta.get("other_response"):
        for tr_query in response.meta.get('detail'):
            each_tr = []
            for td_query in tr_query:
                each_td = ''
                if isinstance(td_query, basestring):
                    each_td = sel.xpath(td_query).xpath('string(.)').extract()[0] \
                        if sel.xpath(td_query).xpath('string(.)') else ''
                elif isinstance(td_query, dict):
                    #xpath 和 input其中一项必不为空
                    #regex 是对xpath里的包括<span> <div>等元素符号里的文本进行搜索。
                    if td_query.get('input'):
                        each_td = td_query.get('input')
                    else:
                        regex_from = response.body
                        if td_query.get('xpath'):
                            regex_from = sel.xpath(td_query.get('xpath')).extract()[0] \
                                if sel.xpath(td_query.get('xpath')).extract() else regex_from
                        if td_query.get('regex'):
                            each_td = re.findall(td_query.get('regex'), regex_from)[0] \
                                if re.findall(td_query.get('regex'), regex_from) else ''
                            # else:
                            #     each_td = sel.xpath(td_query.get('xpath') + '/text()').extract()[0] \
                            #         if sel.xpath(td_query.get('xpath') + '/text()').extract() else ''

                each_tr.append(each_td)
            tr_list.append(each_tr)
            '''
            detail 为list有两种情况，即是否有other_response。以下是有other_response且==json的处理
            '''
    elif isinstance(response.meta.get('detail'), list) \
            and response.meta.get("other_response") == 'json':
        for tr_query in response.meta.get('detail'):
            each_tr = []
            #每个td都可以通过eval得到，或是regex、input得到
            for td_query in tr_query:
                each_td = ''
                if isinstance(td_query, basestring):
                    try:
                        each_td = eval(td_query)
                    except:
                        each_td = ''
                    if isinstance(each_td,(tuple,list)):
                        each_td = ','.join(each_td)
                elif isinstance(td_query, dict):
                    if td_query.get('input'):
                        each_td = td_query.get('input')
                    else:
                        regex_from = response.body
                        if td_query.get("xpath"):
                            regex_from = response.selector.xpath(td_query.get("xpath")).extract()[0] \
                                if response.selector.xpath(td_query.get("xpath")) else regex_from
                        if td_query.get('regex'):
                            each_td = re.findall(td_query.get('regex'), regex_from)[0] \
                                if re.findall(td_query.get('regex'), regex_from) else ''

                each_tr.append(each_td)
            tr_list.append(each_tr)

    #common add 'tr0'
    if response.meta.get('tr_0'):
        tr_list.insert(0, response.meta.get('tr_0'))

    #filter. list like['','',''] will be removed from tr_list
    tr_list = filter(lambda x:filter(lambda y:y, x), tr_list)
    # print 'tr_list done'

    '''
    由tr_list得到item的相应detail_list。格式为detail:[{},{},{}]
    '''
    detail_list = []
    tr_0 = tr_list[0]
    for num in range(1, len(tr_list)):
        each_tr = tr_list[num]
        adict = {}
        adict[tr_0[0]] = each_tr[0]
        for i in range(1, len(each_tr)):
            if tr_0[i] == tr_0[i - 1]:
                if each_tr[i] != adict[tr_0[i - 1]]:
                    adict[tr_0[i]] += each_tr[i]
                else:
                    pass
            else:
                adict[tr_0[i]] = each_tr[i]
        detail_list.append(adict)
    # print 'detail_list done'
    return detail_list

def parse_single_item_from_json(item,response,sel):

    for i in ['balance','issue','open_time','result','sales']:
        try:
            item[i] = eval(response.meta.get(i))
        except:
            item[i] = ''
            print 'eval error'
    item['name'] = response.meta.get('name')
    item['key'] = response.meta.get('key')
    item['src'] = response.meta.get('src')
    item['url'] = response.url

    detail_list = get_detail_list(sel, response) if response.meta.get('detail') else ''
    item['detail'] = detail_list
    return item

def parse_multiple_items(response,sel):
    pass






