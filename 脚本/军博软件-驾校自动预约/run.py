# -*- coding: utf-8 -*-
import requests
import json
import time
import datetime
from multiprocessing import Pool

user='15802111111'
passwd='15802111111'
times={
	'07:30-08:00':'sjd201705020002',
	'08:00-08:30':'sjd2016012600072',
	'08:30-09:00':'sjd2016012600092',
	'09:00-09:30':'sjd2016012600102',
	'09:30-10:00':'sjd2016012600122',
	'10:00-10:30':'sjd2016012600142',
	'10:30-11:00':'sjd2016012600162',
	'11:00-11:30':'sjd2016012600172',
	'15:00-15:30':'sjd2016080800032',
	'15:30-16:00':'sjd2016080800042',
	'16:00-16:30':'sjd2017011100022',
	'16:30-17:00':'sjd2017011100032',
	'17:00-17:30':'sjd2017020900022',
	'17:30-18:00':'sjd201703020002',
	'18:00-18:30':'sjd201705020003',
}
cars={
'8':"ygd201601270009",# 8号车
'7':"ygd201601260010",# 7号车
}

headers={
	'User-Agent': 'Mozilla/5.0',
	'Content-Type':'application/json; charset=utf-8',
	'Accept-Encodin':'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
	'Host':'yymqzyjx.ay001.net',
	'Origin':'http://yymqzyjx.ay001.net',
	'Pragma':'no-cache',
}

def login():
	loginData={
		'UserName':user,
		'Password':passwd,
		'LoginType':0
	}
	loginurl='http://yymqzyjx.ay001.net/Server/AccountServer.asmx/MobileLogin'
	s=requests.Session()
	login=s.post(loginurl,headers=headers,data=json.dumps(loginData))
	ret=login.json()['d']
	if(not ret['isSuccess']):
		print(ret['Message'])
		exit()
	return s
def wait(s):
	fdata={}
	furl='http://yymqzyjx.ay001.net/Server/OrderCoachServer.asmx/GetRandomWaitTimes'
	first=s.post(furl,headers=headers,data=json.dumps(fdata))
	ret=json.loads(first.json()['d'])
	if(not ret['isSuccess']):
		print(ret['Message'])
		return False
	time.sleep(ret['Data'])
	return True

def order(date,carNum,timeNum):
	s=login()
	if(not wait(s)):
		return {'isSuccess':False,'Message':"wait error"}
	sdata={"tbTimeNo":timeNum,"trainDate":date,"coachNo":carNum,"subID":"2"}
	surl='http://yymqzyjx.ay001.net/Server/OrderCoachServer.asmx/orderCoach'
	r = s.post(surl,headers=headers,data=json.dumps(sdata))
	ret=r.json()['d']
	return ret

pool=Pool()
orderSuccess=0

def asncy_order(timeNumA,timeNumB):
	global pool
	global orderSuccess
	date=datetime.date.today() + datetime.timedelta(days=1)
	orderDay=date.strftime("%Y-%m-%d")
	ret=[]
	ret.append(pool.apply_async(order, (orderDay,cars['8'],times[timeNumA])))
	ret.append(pool.apply_async(order, (orderDay,cars['8'],times[timeNumB])))
	ret.append(pool.apply_async(order, (orderDay,cars['7'],times[timeNumA])))
	ret.append(pool.apply_async(order, (orderDay,cars['7'],times[timeNumB])))
	for i in ret:
		t=i.get()
		print("%s:%s"%(timeNumA,t['Message']))
		if(t['isSuccess']):
			orderSuccess+=1
			if(orderSuccess>=2):
				exit()

def main():
	now=datetime.datetime.now()
	print("运行时间:%s"%(now.strftime("%Y-%m-%d %H:%M:%S")))
	global pool
	asncy_order("08:30-09:00","09:30-10:00")
	asncy_order("08:00-08:30","09:00-09:30")
	asncy_order("10:00-10:30","10:30-11:00")
	asncy_order("15:00-15:30","16:00-16:30")
	asncy_order("15:30-16:00","16:30-17:00")
	asncy_order("17:00-17:30","17:30-18:00")
	asncy_order("17:30-18:00","18:00-18:30")
	pool.close()
	pool.join()

if __name__ == '__main__':
	main()