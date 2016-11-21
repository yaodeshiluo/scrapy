import json
import re

def get_crawl_list(category):
    alist=[]
    with open(r'D:\virtualenv\caipiao\v1\v1\spiders\query.json', 'r') as f:
        query = json.load(f)
        if '&&' in category:
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
    if response.url == 'http://www.cwl.gov.cn/kjxx/ssq/hmhz/':
        alist = []
        baseurl = 'http://www.cwl.gov.cn/kjxx/ssq/kjgg/'
        for i in url_list_raw.extract():
            url = baseurl + i.split('/')[-1]
            alist.append(url)
        return alist
    elif response.url == 'http://caipiao.163.com/award/ssq/':
        alist = []
        latest_num = url_list_raw.xpath('text()').extract()[0]
        for i in range(20):
            url = response.url + '%s'%(int(latest_num) - i) + '.html'
            alist.append(url)
        return alist
    else:
        pass
    print 'no handle'

    return url_list_raw.extract()

def get_detail_list(sel,response):
    detail_list = []
    tr1 = sel.xpath(response.meta.get('detail') + '//tr[1]/th/text()').extract()
    # tr1 = sel.xpath(meta.get('detail') + '//tr[1]/th/text()').extract()
    for i in range(1, len(sel.xpath(response.meta.get('detail') + '//tr'))):
        # len(sel.xpath(meta.get('detail') +'//tr'))
        each_tr = sel.xpath(response.meta.get('detail') + '//tr[%s]/td/text()' % (i + 1)).extract()
        # sel.xpath(meta.get('detail') +'//tr[%s]/td/text()'%(i+1)).extract()
        adict = {}
        for j in range(len(tr1)):
            adict[tr1[j]] = each_tr[j]
        detail_list.append(adict)
    return detail_list



