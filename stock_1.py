# -*- coding:utf8 -*-
import tushare as ts
import pandas as pd

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import datetime

'''
----------------------------------股票信息模块------------------------------------------
'''

class Stock(object):

    def __init__(self, code):
        self.code = code

    def get_name(self):
        rtprice = ts.get_realtime_quotes(str(self.code))
        name = rtprice.name
        return name[0]

    def rt_price(self):
        rtprice = ts.get_realtime_quotes(str(self.code))
        rtprice = rtprice.price
        rtprice = float(rtprice[0])
        return rtprice
        #浮点型前复权价格

    def me18(self):
        dkdata = ts.get_k_data(str(self.code))
        dkdata = dkdata.set_index('date')
        close = pd.Series(dkdata.close)
        me_18 = pd.rolling_mean(close, 18)#Serise
        me_18 = me_18.tail(1)
        me_18 = round(float(me_18[0]), 2)
        return me_18
        #浮点型18日均线价格

'''
---------------------------------状态判断模块-------------------------------------------
'''

def nowstuts(rtprice, me18):
    if rtprice > me18:
        return 1
    else:
        return 0

def deter_dev(nstuts, hstuts):
    if nstuts == hstuts:
       return 0
    else:
        if nstuts > hstuts:
            return 1
        else:
            return -1

'''
------------------------------------邮件初始设置---------------------------------------
'''
# 发件地址
from_addr = 'punkfisher@sina.com'
password = 'w23256010'
smtp_server = 'smtp.sina.com.cn'
# 收件人地址:
to_addr = '13661803509@139.com, 13002503523@wo.cn'

'''
-------------------------------------主程序-------------------------------------------
'''

if __name__ == '__main__':


    start = datetime.datetime.now()

    pool = ['000711', '000820', '002078', '002236', '002281', '002310', '002583', '002589', '300072', '300136', '300156', '300197', '300285', '300296', '300476', '603579']  # 可迭代对象


    for i in pool:
        cd = i
        st = Stock(cd)
        name = st.get_name()
        name = name.encode('utf-8', 'ignore')

        rtprice = st.rt_price()
        me18 = st.me18()

        f = open('/home/fisher/PycharmProjects/easytrader_test/stock/' + str(cd) + '.txt', 'r')
        try:
            all_text = f.read()
        finally:
            f.close()
        hisstuts = int(all_text)
        nstuts = nowstuts(rtprice, me18)

        deter = deter_dev(nstuts, hisstuts)
        #短信判断函数，1为发送上穿信息，-1发送下穿信息，0不发信息

        msg = MIMEText(' ', 'plain', 'utf-8')
        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr((Header(name, 'utf-8').encode(), addr))
        # 发件人小魏
        msg['From'] = _format_addr('小魏<%s>' % from_addr)
        # 收件人随便
        msg['To'] = _format_addr(to_addr)
        #
        # server = smtplib.SMTP(smtp_server, 25)
        # server.set_debuglevel(1)
        # server.login(from_addr, password)
        #
        # if deter == 1:
        #     print('%str'%str(cd) + '现价：%s'%str(rtprice) + 'ME18:%s'%str(me18))
        #     msg['Subject'] = Header('%s'%str(cd) +'上穿ME18,现价'+'%s' %str(rtprice), 'utf-8').encode()
        #     server.sendmail(from_addr, [to_addr], msg.as_string())
        # elif deter == -1:
        #     print('%str'%str(cd) + '现价：%s'%str(rtprice) + 'ME18:%s'%str(me18))
        #     msg['Subject'] = Header('%s'%str(cd) +'下穿ME18,现价'+'%s' %str(rtprice), 'utf-8').encode()
        #     server.sendmail(from_addr, [to_addr], msg.as_string())
        # else:
        #     print('%str'%str(cd) + ' current price: %s'%str(rtprice) + ';ME18: %s'%str(me18))
        # server.quit()

        if deter != 0:
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            if deter == 1:
                print('%s'%name + '%s'%str(cd) + '现价：%s'%str(rtprice) + 'ME18:%s'%str(me18))
                msg['Subject'] = Header('%s'%name + '%s'%str(cd) +'上穿ME18,现价'+'%s' %str(rtprice), 'utf-8').encode()
                server.sendmail(from_addr, [to_addr], msg.as_string())
                server.quit()
            else:
                print('%s'%name + '%s'%str(cd) + '现价：%s'%str(rtprice) + 'ME18:%s'%str(me18))
                msg['Subject'] = Header('%s'%name +'%s'%str(cd) +'下穿ME18,现价'+'%s' %str(rtprice), 'utf-8').encode()
                server.sendmail(from_addr, [to_addr], msg.as_string())
                server.quit()
        else:
            print('%str'%str(cd) + ' current price: %s'%str(rtprice) + ';ME18: %s'%str(me18))


        f = open('/home/fisher/PycharmProjects/easytrader_test/stock/' + str(cd) + '.txt', 'w+')
        f.write(str(nstuts))
        f.close()

    end = datetime.datetime.now()
    print end
    print 'Process Time:'
    print (end - start)