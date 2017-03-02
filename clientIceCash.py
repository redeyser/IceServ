#n!/usr/bin/python
# -*- coding: utf-8

"""
    Web Client for IceServ
    License GPL
    writed by Romanenko Ruslan
    redeyser@gmail.com
"""
import my
import httplib, urllib
from dIceServ import PATH_DOWNLOAD_PRICE

_USER='kassir'
_PASSWORD='766766'
_PORT=10110

class IceCashClient:

    def __init__(self,db,regid,idplace,nkassa):
        self.db=db
        self.regid      = regid
        self.idplace    = idplace
        self.nkassa     = nkassa

    def verify(self):
        if not self.db._regs_get(regid=self.regid):
            return False
        self.idreg=self.db.reg['id']
        if not self.db._kasses_find(self.idreg,self.idplace,self.nkassa):
            return False
        self.idkassa=self.db.kassa['id']
        self.idprice=self.db.kassa['idprice']
        self.ip=self.db.kassa['ip']
        return True

    def get_price(self):
        if not self.db._prices_get(self.idreg,self.idprice):
            return False
        if self.db.price['date']==None or self.db.price['time']==None:
            return False
        if self.db.kassa['date']==None or self.db.price['time']==None:
            kassa_time=0
        else:
            kassa_time=my.mydt2time(str(self.db.kassa['date']),str(self.db.kassa['time']))

        price_time=my.mydt2time(str(self.db.price['date']),str(self.db.price['time']))
        #print str(self.db.price['date']),str(self.db.price['time']),str(self.db.kassa['date']),str(self.db.kassa['time'])
        if kassa_time>price_time:
            return False
        return True

    def set_price(self):
        dt=my.curdate2my()
        tm=my.curtime2my()
        self.db._kasses_upd(self.idreg,self.idkassa,{'date':dt,'time':tm})
        return True

    def time_update(self,struct={}):
        dt=my.curdate2my()
        tm=my.curtime2my()
        struct['up_date'] = dt
        struct['up_time'] = tm
        self.db._kasses_upd(self.idreg,self.idkassa,struct)
        return True

    def connect(self):
        try:
            self.conn = httplib.HTTPConnection("%s:%d" % (self.ip,_PORT))
            return True
        except:
            print "not connect"
            return False


    def get(self,_type,page,params):
        self.data=""
        if not self.connect():
            print "error connect"
            return False
        params.update({"_user":_USER,"_password":_PASSWORD})
        if _type=='GET':
            p=''
            for k,v in params.items():
                if p!='':
                    p+='&'
                p+="%s=%s" %(k,v)
            page=page+"?"+p
        params=urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/xml"}
        try:
            self.conn.request(_type,page,params,headers)
            response = self.conn.getresponse()
            if response.status!=200:
                print "error_status"
                return False
            self.data=response.read()
        except:
            print "error get data"
            return False
        finally:
            self.conn.close()
        return True

    def trsc_add(self,data):
        r=0
        ups=[]
        lastid=0
        for d in data:
            #print d
            hd=d['h']
            cts=d['b']
            _id=hd[0]
            dt=hd[3]
            tm=hd[4]
            hd=hd[3:]
            hd[21]=0
            #print hd
            if not self.db._trsc_find(self.idreg,self.idplace,self.nkassa,dt,tm,_id):
                idx=[self.idreg,self.idplace,self.nkassa,_id]
                hd=idx+hd
                if not self.db._trsc_add(hd,cts):
                    break
            else:
                pass

            lastid=_id
            if len(ups)==0:
                ups.append(_id)

        if len(ups)!=0:
            ups.append(lastid)
        return ups

    def Zet_add(self,data):
        r=0
        ups=[]
        for d in data:
            hd=d['head']
            cts=d['body']
            hd['_id']=hd['id']
            hd['up']=0
            del hd['id']
            hd['idreg']     = self.idreg
            hd['idplace']   = self.idplace
            hd['nkassa']    = self.nkassa
            if not self.db._Zet_find(self.idreg,self.idplace,self.nkassa,hd['date'],int(hd['_id'])):
                if self.db._Zet_add(hd,cts):
                    r+=1
                    ups.append(hd['_id'])
            else:
                self.db.run(self.db.tb_Zet_cont._del(self.idreg,self.idplace,self.nkassa,int(self.db.Zet['id'])))
                self.db._Zet_upd(self.idreg,self.idplace,self.nkassa,int(self.db.Zet['id']),hd)
                hd['id']=int(self.db.Zet['id'])
                if self.db._Zet_add(hd,cts,withouthd=True):
                    r+=1
                    ups.append(hd['_id'])
        return ups
        
