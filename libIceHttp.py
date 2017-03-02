#!/usr/bin/python
# -*- coding: utf-8

import httplib, urllib,time
import json

class IceClient:

    def __init__(self,server_ip,server_port,user,password):
        self.server_ip=server_ip
        self.server_port=server_port
        self.user=user
        self.password=password

    def connect(self):
        try:
            self.conn = httplib.HTTPConnection("%s:%d" % (self.server_ip,self.server_port))
            return True
        except:
            print "not connect"
            return False

    def get_file(self,page,fn):
        return urllib.urlretrieve(page, fn)

    def get(self,_type,page,params):
        self.data=""
        if not self.connect():
            print "error connect"
            return False
        params.update({"_user":self.user,"_password":self.password})
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

    def get_regs_sets(self):
        return self.get('GET','/cmd/regs_sets',{})

    def send_regs_sets(self,sets):
        jsets=json.dumps(sets,ensure_ascii=False)
        return self.get('POST','/cmd/regs_sets',{'sets':jsets})


ic = IceClient("localhost",10101,"beerkem","766766")
ic.connect()
ic.get_regs_sets()
print ic.data
sets={'temperature':0.41}
ic.send_regs_sets(sets)
#if ic._get_regs_sets('temperature'):
#    print ic.set_value


