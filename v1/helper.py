# coding: utf-8
import json
import re
from scrapy.utils.url import urljoin_rfc

def get_crawl_list(category):
    alist=[]
    with open(r'D:\virtualenv\caipiao\v1\v1\spiders\query.json', 'r') as f:
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
        return alist

    print 'no handle'
    print 'url_list is',url_list_raw.extract()
    url_list = []
    for url in url_list_raw.extract():
        full_url = response.urljoin(url)
        url_list.append(full_url)



    return url_list

def get_detail_list(sel,response):
    tr_list = []
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

    elif isinstance(response.meta.get('detail'), list) \
            and not response.meta.get("other_response"):
        for tr_query in response.meta.get('detail'):
            each_tr = []
            for td_query in tr_query:
                each_td = None
                if isinstance(td_query, basestring):
                    each_td = sel.xpath(td_query).xpath('string(.)').extract()
                elif isinstance(td_query, dict):
                    if td_query.get('xpath'):
                        if td_query.get('regex'):
                            each_td = sel.xpath(td_query.get('xpath')).xpath('string(.)').extract()[0]
                            each_td = re.findall(td_query.get('regex'), each_td)[0] if re.findall(td_query.get('regex'), each_td) else ''
                        else:
                            each_td = sel.xpath(td_query.get('xpath') + '/text()').extract()[0]
                    if td_query.get('input'):
                        each_td = td_query.get('input')
                each_tr.append(each_td)
            tr_list.append(each_tr)
    elif isinstance(response.meta.get('detail'), list) \
            and response.meta.get("other_response") == 'json':

        for tr_query in response.meta.get('detail'):
            each_tr = []
            for td_query in tr_query:
                each_td = None
                if isinstance(td_query, basestring):
                    each_td = eval(td_query) if eval(td_query) else ''
                    if isinstance(each_td,(tuple,list)):
                        each_td = ','.join(each_td)
                elif isinstance(td_query, dict):
                    if td_query.get('regex'):
                        each_td = re.findall(td_query.get('regex'), response.body)[0] if re.findall(td_query.get('regex'), response.body) else ''
                    if td_query.get('input'):
                        each_td = td_query.get('input')
                each_tr.append(each_td)
            tr_list.append(each_tr)

    #common add 'tr0'
    if response.meta.get('tr_0'):
        tr_list.insert(0, response.meta.get('tr_0'))

    #filter. list like['','',''] will be removed from tr_list
    tr_list = filter(lambda x:filter(lambda y:y, x), tr_list)
    # print tr_list

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
    return detail_list







