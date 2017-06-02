# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 10:25:40 2017

@author: 42135
"""

import urllib.request
import urllib
import http.cookiejar
import json
import re
import time
import numpy as np

ID = '手机号'
pswd = '密码'
hospitalId = '129' # 医院ID
departmentId = '200001189' # 科室ID
doctorName = '李晓娟' # 按医生名挂号
#doctorTitleName = '副主任号' # 按医生头衔挂号
dutyCode = ['1', '2'] # 1 是上午， 2是下午
dutyDate = ['2017-06-05', '2017-06-06', '2017-06-07', '2017-06-08', '2017-06-09']
hospitalCardId = '' # 就医卡？不知道有什么用
medicareCardId = '' # 医保卡，无则为空字符串
codeIndex = 0
dateIndex = 0
global doctorId
global dutySourceId
global patientId


def get_opener(head):
    cj = http.cookiejar.CookieJar()
    pro = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(pro)
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener

# 模拟浏览器
header = {
        'Connection': 'Keep-Alive',
        'Accept-Language': 'en-US, en;q=0.8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.bjguahao.gov.cn'
        }
opener = get_opener(header)

# 登录
loginUrl = 'http://www.bjguahao.gov.cn/quicklogin.htm'
loginDict = {
        'mobileNo': ID,
        'password': pswd,
        'yzm': '',
        'isAjax': 'true'
        }
loginPost = urllib.parse.urlencode(loginDict).encode()
loginOp = opener.open(loginUrl, loginPost)
loginData = json.loads(loginOp.read())
if loginData['hasError'] == True:
    raise ValueError(loginData['msg'])

# 挂号查询
registerUrl = 'http://www.bjguahao.gov.cn/dpt/partduty.htm'
times = 1 # 查询次数
while 1:
    print('查询次数\t%s' % times)
    flag = 0
    registerDict = {
            'hospitalId': hospitalId,
            'departmentId': departmentId,
            'dutyCode': dutyCode[codeIndex % 2],
            'dutyDate': dutyDate[dateIndex % 5], # 5天轮流查询
            'isAjax': 'true'
            }
    registerPost = urllib.parse.urlencode(registerDict).encode()
    registerOp = opener.open(registerUrl, registerPost)
    registerData = json.loads(registerOp.read())
    if registerData['hasError'] == True:
        raise ValueError(registerData['msg'])
    msg = registerData['data']
    print('正在搜索余号信息, 目标日期\t%s\n, 时间\t%s\n' % (dutyDate[dateIndex % 5], dutyCode[codeIndex % 2]))
    if len(msg) == 0:
        print('尚未放号，将查询其他时间')
        time.sleep(np.random.rand(10, 1)[0] + 1)
        continue
    for doctorInfor in msg:
        # 按医生名字挂号
        if doctorInfor['doctorName'] == doctorName:
            print('医生\t%s' % doctorName)
            if doctorInfor['remainAvailableNumber'] > 0:
                print('号余量:\t%s\n' % doctorInfor['remainAvailableNumber'])
                doctorId = str(doctorInfor['doctorId'])
                dutySourceId = str(doctorInfor['dutySourceId'])
                flag = 1
                break
            else:
                print('没号了,日期%s\n' % (dutyDate[dateIndex % 5]))
                
        else:
            print('医生:%s\n号余量:\t%s\n' % (doctorInfor['doctorName'], doctorInfor['remainAvailableNumber']))
    # todo 按医生头衔挂号 doctorTitleName
    # todo 按医生技能挂号 skill
    if flag == 1:
        break
    else:
        time.sleep(np.random.rand(10, 1)[0] + 1)
        codeIndex += 1
        if codeIndex % 2 == 0:
            dateIndex += 1
    times += 1
           
# 找patientId
rabbitUrl = 'http://www.bjguahao.gov.cn/order/confirm/'+hospitalId+'-'+departmentId+'-'+doctorId+'-'+dutySourceId+'.htm'
rabbitOp = opener.open(rabbitUrl).read()
find = re.search('.*<input type=\\"radio\\" name=\\"hzr\\" value=\\"(.*?)\\".*', str(rabbitOp))
patientId = find.group(1)

# 发送验证码
msgCodeUrl = "http://www.bjguahao.gov.cn/v/sendorder.htm"
smsVerifyOp = opener.open(msgCodeUrl, urllib.parse.urlencode('').encode())
smsVerifyData = json.loads(smsVerifyOp.read())
if smsVerifyData['hasError'] == True:
    raise ValueError(smsVerifyData['msg'])
smsVerifyCode = input('Input your verify code:\n')

#挂号
confirmUrl = 'http://www.bjguahao.gov.cn/order/confirm.htm'
confirmDict = {
        'dutySourceId': dutySourceId,
        'hospitalId': hospitalId,
        'departmentId': departmentId,
        'doctorId': doctorId,
        'patientId': patientId,
        'hospitalCardId': hospitalCardId,
        'medicareCardId': medicareCardId,
        'reimbursementType': '-1',
        'smsVerifyCode': smsVerifyCode,
        'childrenBirthday': '',
        'isAjax': 'true'
        }
confirmMsg = opener.open(confirmUrl, urllib.parse.urlencode(confirmDict).encode())
confirmData = json.loads(confirmMsg.read())
print(confirmData['msg'])