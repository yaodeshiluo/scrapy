# coding: utf-8
import json
import re

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
    special_urls_1 = {'http://www.cwl.gov.cn/kjxx/ssq/hmhz/':'http://www.cwl.gov.cn/kjxx/ssq/kjgg/',
                    'http://www.lecai.com/lottery/draw/list/50':'http://www.lecai.com/lottery/draw/view/',
                      'http://www.cwl.gov.cn/kjxx/fc3d/hmhz/':'http://www.cwl.gov.cn/kjxx/fc3d/kjgg/',
                      'http://www.cwl.gov.cn/kjxx/qlc/hmhz/':'http://www.cwl.gov.cn/kjxx/qlc/kjgg/',
                      'http://www.lottery.gov.cn/historykj/history.jspx?page=false&_ltype=dlt&termNum=30&startTerm=&endTerm=':'http://www.lottery.gov.cn/kjdlt/'}
    #/html/body/div[7]/div[1]/table/tbody/tr[position()>=1 and position()<=2]/td[1]/a/@href
    #url_list_raw = response.selector.xpath('/html/body/div[7]/div[1]/table/tbody/tr[position()>=1 and position()<=2]/td[1]/a/@href')
    special_urls_2 = {'http://kjh.cailele.com/kj_ssq.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=100&term=%s',
                      'http://www.lecai.com/lottery/draw/list/52':'http://www.lecai.com/lottery/draw/ajax_get_detail.php?lottery_type=52&phase=%s',
                      'http://www.lecai.com/lottery/draw/view/1':'http://www.lecai.com/lottery/draw/ajax_get_detail.php?lottery_type=1&phase=%s',
                      'http://kjh.cailele.com/kj_3d.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=102&term=%s',
                      'http://kjh.cailele.com/kj_dlt.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=1&term=%s',
                      'http://caipiao.163.com/award/3d/':'http://caipiao.163.com/award/3d/%s.html',
                      'http://caipiao.163.com/award/qlc/':'http://caipiao.163.com/award/qlc/%s.html',
                      'http://caipiao.163.com/award/dlt/':'http://caipiao.163.com/award/dlt/%s.html',
                      'http://caipiao.163.com/award/ssq/':'http://caipiao.163.com/award/ssq/%s.html',
                      'http://www.zhcw.com/kaijiang/zhcw_qlc_index.html':'http://kaijiang.zhcw.com/zhcw/html/qlc/detail_%s.html',
                      'http://kjh.cailele.com/kj_qlc.shtml':'http://kjh.cailele.com/common/kjgg.php?lotType=101&&term=%s'}
    if special_urls_1.get(response.url):
        baseurl = special_urls_1.get(response.url)
        alist = []
        for i in url_list_raw.extract():
            url = baseurl + i.split('/')[-1]
            alist.append(url)
        return alist
    elif special_urls_2.get(response.url):
        baseurl = special_urls_2.get(response.url)
        alist = []
        # latest_num = url_list_raw.xpath('text()').extract()[0]
        for i in url_list_raw.extract():
            url = baseurl%(i)
            alist.append(url)
        return alist
    else:
        pass
    print 'no handle'
    print 'url_list is',url_list_raw.extract()

    return url_list_raw.extract()

def get_detail_list(sel,response):
    special_urls_1 = {'http://kjh.cailele.com/kj_3d.shtml':'',
                      "http://kjh.cailele.com/kj_ssq.shtml":'',
                      'http://kjh.cailele.com/kj_qlc.shtml':'',
                      'http://kjh.cailele.com/kj_dlt.shtml':{u'一等奖/基本':'prize1',
                                                             u'一等奖/追加':'prize2',
                                                             u'二等奖/基本':'prize3',
                                                             u'二等奖/追加':'prize4',
                                                             u'三等奖/基本':'prize5',
                                                             u'三等奖/追加':'prize6',
                                                             u'四等奖/基本':'prize7',
                                                             u'四等奖/追加':'prize13',
                                                             u'五等奖/基本':'prize8',
                                                             u'五等奖/追加':'prize14',
                                                             u'六等奖/基本':'prize9'}}
    if response.meta.get('detail') in special_urls_1:
        info = response.selector.xpath('//input[3]/@value').extract()
        detail_list = []
        for each in info[0].split('#'):
            adict = {}
            each_split = each.split('^')
            adict[each_split[0]] = each_split[1]+u'注' + u'(每注' +each_split[-1] + u'元)'
            detail_list.append(adict)
        return detail_list

    detail_list = []
    tr1 = sel.xpath(response.meta.get('detail') + '//tr[1]/*/text()').extract()
    down_num = 0
    if len(tr1) < 3:
        tr1 = sel.xpath(response.meta.get('detail') + '//tr[2]/*/text()').extract()
        down_num += 1
    if response.meta.get('col_span'):
        from copy import deepcopy
        col_span = response.meta.get('col_span')
        tr1_copy = deepcopy(tr1)
        for i in col_span:
            add = ''.join([tr1_copy[i],u'_'])
            tr1.insert(tr1.index(tr1_copy[i])+1,add)
    num = 0 + down_num
    append = None
    for i in range(1+down_num, len(sel.xpath(response.meta.get('detail') + '//tr'))):
        num += 1
        # len(sel.xpath(meta.get('detail') +'//tr'))
        each_tr = sel.xpath(response.meta.get('detail') + '//tr[%s]/td' % (i + 1)).xpath('string(.)').extract()
        # sel.xpath(meta.get('detail') +'//tr[%s]/td/text()'%(i+1)).extract()
        if len(each_tr) < 3:
            pass
        else:
            if response.meta.get('row_span'):
                if num in response.meta.get('row_span'):
                    append = each_tr[0]
                else:
                    if append:
                        each_tr.insert(0,append)

            adict = {}

            for j in range(len(tr1)):
                adict[tr1[j]] = each_tr[j]
            detail_list.append(adict)
    return detail_list



