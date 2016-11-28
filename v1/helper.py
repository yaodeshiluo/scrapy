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
    # if response.url == 'http://www.cwl.gov.cn/kjxx/ssq/hmhz/':
    #     alist = []
    # special_urls_1 = {#'http://www.cwl.gov.cn/kjxx/ssq/hmhz/':'http://www.cwl.gov.cn/kjxx/ssq/kjgg/',
    #                 'http://www.lecai.com/lottery/draw/list/50':'http://www.lecai.com/lottery/draw/view/',
    #                   'http://www.cwl.gov.cn/kjxx/fc3d/hmhz/':'http://www.cwl.gov.cn/kjxx/fc3d/kjgg/',
    #                   'http://www.cwl.gov.cn/kjxx/qlc/hmhz/':'http://www.cwl.gov.cn/kjxx/qlc/kjgg/',
    #                   'http://www.lottery.gov.cn/historykj/history.jspx?page=false&_ltype=dlt&termNum=30&startTerm=&endTerm=':'http://www.lottery.gov.cn/kjdlt/'}
    #/html/body/div[7]/div[1]/table/tbody/tr[position()>=1 and position()<=2]/td[1]/a/@href
    #url_list_raw = response.selector.xpath('/html/body/div[7]/div[1]/table/tbody/tr[position()>=1 and position()<=2]/td[1]/a/@href')
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
    # if special_urls_1.get(response.url):
    #     baseurl = special_urls_1.get(response.url)
    #     alist = []
    #     for i in url_list_raw.extract():
    #         url = baseurl + i.split('/')[-1]
    #         alist.append(url)
    #     return alist

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
    # special_urls_1 = {'http://kjh.cailele.com/kj_3d.shtml':'',
    #                   "http://kjh.cailele.com/kj_ssq.shtml":'',
    #                   'http://kjh.cailele.com/kj_qlc.shtml':'',
    #                   'http://kjh.cailele.com/kj_dlt.shtml':{u'一等奖/基本':'prize1',
    #                                                          u'一等奖/追加':'prize2',
    #                                                          u'二等奖/基本':'prize3',
    #                                                          u'二等奖/追加':'prize4',
    #                                                          u'三等奖/基本':'prize5',
    #                                                          u'三等奖/追加':'prize6',
    #                                                          u'四等奖/基本':'prize7',
    #                                                          u'四等奖/追加':'prize13',
    #                                                          u'五等奖/基本':'prize8',
    #                                                          u'五等奖/追加':'prize14',
    #                                                          u'六等奖/基本':'prize9'},
                      # 'http://kjh.cailele.com/kj_p3.shtml':{u'直选':'prize1',
                      #                                       u'组选三':'prize2',
                      #                                       u'组选六':'prize3'}
                      # }
    # if response.meta.get('detail') in special_urls_1:
    #     info = response.selector.xpath('//input[3]/@value').extract()
    #     detail_list = []
    #     for each in info[0].split('#'):
    #         adict = {}
    #         each_split = each.split('^')
    #         adict[each_split[0]] = each_split[1]+u'注' + u'(每注' +each_split[-1] + u'元)'
    #         detail_list.append(adict)
    #     return detail_list

    # detail_list = []
    # tr_list = []
    # col_span = None
    # if response.meta.get('col_span'):
    #     col_span = response.meta.get('col_span')
    # tr1 = sel.xpath(response.meta.get('detail') + '//tr[1]/*/text()').extract()
    # down_num = 0
    # if len(tr1) < 3:
    #     tr1 = sel.xpath(response.meta.get('detail') + '//tr[2]/*/text()').extract()
    #     down_num += 1
    # if col_span and down_num in col_span:
    #     from copy import deepcopy
    #     tr1_copy = deepcopy(tr1)
    #     add = ''.join([tr1_copy[0],u'_'])
    #     tr1.insert(tr1.index(tr1_copy[0])+1,add)
    # num = 0 + down_num
    # append = None
    # tr1_length = len(tr1)
    # for i in range(down_num + 1, len(sel.xpath(response.meta.get('detail') + '//tr'))):
    #     num += 1
    #     # len(sel.xpath(meta.get('detail') +'//tr'))
    #     each_tr = sel.xpath(response.meta.get('detail') + '//tr[%s]/td' % (i + 1)).xpath('string(.)').extract()
    #     # sel.xpath(meta.get('detail') +'//tr[%s]/td/text()'%(i+1)).extract()
    #     if len(each_tr) < 3:
    #         pass
    #     else:
    #         if col_span and num in col_span:
    #             from copy import deepcopy
    #             each_tr_copy = deepcopy(each_tr)
    #             add = ''.join([each_tr_copy[0], u'_'])
    #             each_tr.insert(each_tr.index(each_tr_copy[0]) + 1, add)
    #         if len(each_tr) == tr1_length:
    #             append = each_tr[0]
    #         else:
    #             if append:
    #                 each_tr.insert(0,append)
    #
    #         adict = {}
    #
    #         for j in range(len(tr1)):
    #             adict[tr1[j]] = each_tr[j]
    #         detail_list.append(adict)
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
                        for i in int(each_td.xpath('@colspan').extract()):
                            each_tr.append(each_td.xpath('string(.)').extract()[0])
                    else:
                        each_tr.append(each_td.xpath('string(.)').extract()[0])
                    if each_td.xpath('@rowspan'):
                        append = each_td.xpath('string(.)').extract()[0]

                tr_list.append(each_tr)

    elif isinstance(response.meta.get('detail'), list):
        for tr_query in response.meta.get('detail'):
            each_tr = []
            for td_query in tr_query:
                each_td = None
                if isinstance(td_query, basestring):
                    each_td = sel.xpath(td_query).extract()
                elif isinstance(td_query, dict):
                    if td_query.get('xpath'):
                        each_td = sel.xpath(td_query.get('xpath')).extract()[0]
                    if td_query.get('regex'):
                        each_td = re.findall(td_query.get('regex'), each_td)[0] if re.findall(td_query.get('regex'), each_td) else ''
                    if td_query.get('input'):
                        each_td = td_query.get('input')
                each_tr.append(each_td)
            tr_list.append(each_tr)
    #common
    if response.meta.get('tr_0'):
        tr_list.insert(0, response.meta.get('tr_0'))

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







