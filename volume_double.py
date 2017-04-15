# -*- coding:utf-8 -*-
import tushare as ts
import pandas as pd
import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

'''
首先获得成交量较上一日翻倍的列表，然后筛选出在年线上方的股票；
特色：调用两次ts.get_k_data()，只适用于低频策略；

ts.get_k_data()得到的DataFrame说明
kdata
             0      1      2      3      4       5         6
           date   open  close   high    low    volume    code
0    2013-09-02   6.40   6.20   6.52   6.09   34096.0  600848
1    2013-09-03   6.20   6.24   6.36   6.19   23047.0  600848
...
639  2017-04-12  20.26  21.41  22.66  20.26  142753.0  600848
640  2017-04-13  21.30  21.43  21.80  21.02   77429.0  600848
'''

'''
-------------------------------------------获得所有在basic表中的股票代码---------------------------------------
'''
#获取所有股票的代码
def get_codelist():
    all_info = ts.get_stock_basics()
    CODE_LIST = []
    for i in all_info.index:
        CODE_LIST.append(i)
    return CODE_LIST
'''
------------------------------------------筛选出成交量较昨日翻倍的股票------------------------------------------
'''
def volume_fliter(CODE_LIST):
    volume_double = []
    volume_not_double = []
    error_code = []
    for code in CODE_LIST:
        try:                                                   #报错：停牌/基金/timeout，尚不完全了解某些股票报错的原因
            kdata = ts.get_k_data(code)
            if len(kdata.index) > 1:                           #今天上市的股票不考虑
                if kdata.iloc[-1, 5] >= 2*kdata.iloc[-2, 5]:   #今日成交量超过昨日成交量的两倍
                    volume_double.append(code)
                else:
                    volume_not_double.append(code)
            else:
                pass
        except:
            error_code.append(code)
            print code + '报错'
    return [volume_double, volume_not_double, error_code]

'''
--------------------------------------------筛选出位于年线上方股票------------------------------------------------
'''
def ma250_fliter(CODE_LIST):
    NORMALCODE = []
    OVERMA250 = []
    IPORECENTLY = []
    NOTOVERMA250 = []
    ERRORCODE = []
    for code in CODE_LIST:
        kdata = ts.get_k_data(code)
        try:
            if len(kdata.index) > 250:
                NORMALCODE.append(code)
                kdata = kdata.set_index('date')
                close = pd.Series(kdata.close)
                ma250 = pd.rolling_mean(close, 250)
                if ma250[-1] < close[-1]:
                    OVERMA250.append(code)
                else:
                    NOTOVERMA250.append(code)
            else:
                IPORECENTLY.append(code)
        except:
            ERRORCODE.append(code)
    return [OVERMA250, NOTOVERMA250, NORMALCODE, IPORECENTLY, ERRORCODE]

'''
---------------------------------------------获取邮件正文字符串---------------------------------------------------
'''

def name_str(CODE_LIST):
    ERRORCODE = []
    namestr = '成交量翻倍，年线以上的k股票列表:'
    i = 0
    for code in CODE_LIST:
        if i % 4 == 0:
            namestr += '\n'
        else:
            pass
        i += 1
        try:
            rtprice = ts.get_realtime_quotes(code)
            name = rtprice.iloc[0, 0]
            name = name.encode('utf-8')
            namestr += name
            namestr += ' '
            namestr += code
            namestr += '; '
        except:
            ERRORCODE.append(code)
    return namestr

'''
--------------------------------------------------邮件设置-------------------------------------------------------
'''
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

from_addr = '******************'
password = '*******************'
to_addr_2 = '13661803509@139.com'    #大神的139邮箱
to_addr = '13002503523@wo.cn'        #wo垃圾邮箱
to_addr_3 = 'wzx_fisher@hotmail.com'   #常用邮箱

smtp_server = 'smtp.sina.com.cn'


if __name__ == '__main__':

    CODE_LIST_RAW = get_codelist()
    print 'CODELISTRAW:'
    print CODE_LIST_RAW
    DOUBLE_VOLUME_LIST = volume_fliter(CODE_LIST_RAW)
    print 'DOUBLE_VOLUME_LIST:'
    print DOUBLE_VOLUME_LIST[0]
    OVERMEA250_DOUBLEVOLUME = ma250_fliter(DOUBLE_VOLUME_LIST[0])
    print 'OVERMA250)DOUBLEVOLUME:'
    print OVERMEA250_DOUBLEVOLUME
    text = name_str(OVERMEA250_DOUBLEVOLUME[0])
    print text

    msg = MIMEText('%s' % text, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'小魏 <%s>' % from_addr)
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header(u'年线以上成交量翻倍的股票', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr_2], msg.as_string())
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
