#!/usr/bin/python
# -*- coding: utf-8

"""
    Web Service IceServ 2.0
    License GPL
    writed by Romanenko Ruslan
    redeyser@gmail.com
"""

from   BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from   SocketServer import ThreadingMixIn
from   fhtml import *
from   md5 import md5
import threading
import urlparse
import cgi
import Cookie
import time
import sys,os
import re
import json
import my
import subprocess
PIPE = subprocess.PIPE

import dbIceServ
from clientIceCash import *
from actIceCash import *

MYSQL_HOST  = 'localhost'
VERSION     = '2.0.012'

RULE_NO         = "no"
RULE_SYS        = "sys"
RULE_ADM        = "adm"
RULE_CNT        = "cnt"
POST_TRUE       = "1"
POST_FALSE      = "0"
PATH_DOWNLOAD_PRICE = "/files/download/price"

def gethash(h,key,default):
    if h.has_key(key):
        return h[key]
    else:
        return default


def ice_create_lock ():
    icelock=threading.Lock()

def ice_lock():
    icelock.acquire()

def ice_unlock():
    icelock.release()

def lsdir(dir):
    f=[]
    d=[]
    for (dirpath, dirnames, filenames) in os.walk(dir):
        f.extend(filenames)
        d.extend(dirnames)
        break
    d.sort()
    f.sort()
    return [d,f]

class Handler(BaseHTTPRequestHandler):

    def mysql_open(self):
        self.db = dbIceServ.dbIceServ(dbIceServ.DATABASE, MYSQL_HOST, dbIceServ.MYSQL_USER, dbIceServ.MYSQL_PASSWORD) 
        return self.db.open()
        
    def _getval(self,key,default):
        if self.get_vals.has_key(key):
            return self.get_vals[key]
        else:
            return default

    def _send_false(self):
        self.send_response(404)
        self.end_headers()

    def _send_true(self):
        self.send_response(200)
        self.end_headers()

    def _send_HEAD(self,tp,code=200):
        self.send_response(code)
        self.send_header("Content-type", tp)
        self.end_headers()

    def _send_redirect(self,url):
        self.send_response(302)
        self.send_header('Location', url)

    def wjson(self,j):
        self._send_HEAD("application/json")
        self._write(j)

    def wxml(self,j):
        self._send_HEAD("text/xml")
        self._write(j)

    def whtml(self,j):
        self._send_HEAD("text/html")
        self._write(j)

    def _redirect(self,url):
        self._send_redirect(url)
        self.end_headers()

    def do_HEAD(self):
        self._send_HEAD('text/html')
        self.send_response(200)

    def ReadCookie(self):
        if "Cookie" in self.headers:
            c = Cookie.SimpleCookie(self.headers["Cookie"])
            if c.has_key('login') and c.has_key('password'):
                self.curlogin    = c['login'].value
                self.curpassword = c['password'].value
                return True
            else:
                self.curlogin    = None
                self.curpassword = None
                return False

        else:
            return False

    def GetAuth(self,gets):
        if gets.has_key("_user") and gets.has_key("_password"):
            self.curlogin    = gets['_user']
            self.curpassword = gets['_password']
            return True
        else:
            return False
            
    def PostAuth(self,form):
        if form.has_key("_user") and form.has_key("_password"):
            self.curlogin    = form['_user'].value
            self.curpassword = form['_password'].value
            return True
        else:
            print "not exists password and user"
            return False

    def WriteCookie(self,form):
        if form.has_key("login"):
            c = Cookie.SimpleCookie()
            c['login'] = form["login"].value
            c['password'] = form["password"].value
            self.send_header('Set-Cookie', c.output(header=''))

    def ClearCookie(self):
        c = Cookie.SimpleCookie()
        c['login'] = ""
        c['password'] = ""
        self.send_header('Set-Cookie', c.output(header=''))

    def get_file(self,path="",decode=True):
        if path[0]!='/':
            path='/'+path
        path='site'+path
        try:
            f=open(path,"r")
            message=f.read()
            f.close()
        except:
            message=''
        if decode:
            message=message.decode("utf8")
        return message

    def put_file(self,filedata,path):
        path='site'+path
        try:
            f=open(path,"w")
            f.write(filedata)
            f.close()
            return True
        except:
            return False
            pass
        return 
    
    def pattern_params_get(self,html):
        params={}
        a=re.findall("%%#.*?#.*?%%",html)
        for n in a:
            m=re.search("%%#(.*?)#(.*?)%%",n)
            if m!=None and len(m.groups())==2:
                tag=m.group(1)
                params[tag]=m.group(2)
        return params

    def pattern_rep_arr(self,html,amark,aval):
        return ht_reptags_arr(html,amark,aval)

    def pattern_rep_hash(self,html,h):
        return ht_reptags_hash(html,h)

    def pattern_params_clear(self,html):
        a=re.findall("%%#.*?#.*?%%",html)
        for n in a:
            html=html.replace(n,"")
        a=re.findall("%.*?%",html)
        for n in a:
            html=html.replace(n,"")
        return html

    def _write(self,html):
        self.wfile.write(html.encode("utf8"))

    def write_body(self,b):
        self._send_HEAD("text/html")
        html=self.get_file('/head.html')
        info_user=self.curlogin
        info_ip=self.client_address[0]
        html = ht_reptags_arr(html,["%css%","%version%","%body%"],[self.cur_css,VERSION,b])
        html = ht_reptags_arr(html,["%info_user%","%info_ip%","%info_currule%","%idreg%"],[info_user,info_ip,str(self.currule),str(self.idreg)])
        self._write(html)

    def wbody(self,p):
        self.write_body(self.replace_rulehid(p))

    def _request(self,rule,pattern,alter):
        if self.currule!=rule and rule!="" :
            self._redirect(alter)
            return
        self.wbody(pattern)

    def write_file(self,f):
        self._send_HEAD("application/x")
        html=self.get_file(f,False)
        self.wfile.write(html)

    def verify(self):   
        if self.db._regs_auth(self.curlogin,self.curpassword):
            if self.db.reg['css']!='':
                self.cur_css=self.db.reg['css']
            self.idreg=self.db.reg['id']
            self.currule=self.db.rule
            return True
        else:
            return False

    def replace_rulehid(self,p):
        if self.currule != RULE_ADM:
            hid_adm="hidden"
        else:
            hid_adm=""
        if self.currule != RULE_SYS:
            hid_sys ="hidden"
        else:
            hid_sys=""
        return self.pattern_rep_arr(self.get_file(p),["%hid_noadm%","%hid_nosys%"],[hid_adm,hid_sys])

    def verify_icecash(self):
        if not self.get_vals.has_key('idplace')\
        or not self.get_vals.has_key('nkassa'):
            return False
        else:
            return True

    def verify_icecash_post(self,form):
        if not form.has_key('idplace')\
        or not form.has_key('nkassa'):
            return False
        else:
            return True

    def upload_price(self,f):
        print "upload_file",f
        r=f.rfind('.')
        if r==-1:
            ext=""
            base=f
        else:
            ext=f[r+1:]
            base=f[:r]
        a=base.split("_")
        #print f,ext,base
        if len(a)<2:
            return False
        (regid,price)=a
        if not self.db._regs_get(regid=regid):
            return False
        if not self.db._prices_find(self.db.reg['id'],price):
            return False
        if ext!="zip":
            cmd="zip -j site/files/download/price/%s site/files/download/price/%s" % (base,f)
            p = subprocess.Popen(cmd, shell=True, stdout=PIPE)
            while p.poll()==None:
                pass
            result=p.returncode
            if int(result)!=0:
                return False
            self.db.price_load("site/files/download/price/%s" % f)
            os.remove("site/files/download/price/%s" % f)
        dt=my.curdate2my()
        tm=my.curtime2my()
        self.db._prices_upd(self.db.reg['id'],self.db.price['id'],{'date':dt,'time':tm})
        return True

    def create_icecash(self,db,regid,idplace,nkassa):
        self.icecash=IceCashClient(db,regid,idplace,nkassa)

    def create_actions(self,idreg,db):
        self.actions=Actions(idreg,db)

    """ GET REQUEST 
        ------------
    """    

    def do_GET(self):
        self.cur_css='blue.css'
        parsed_path = urlparse.urlparse(self.path)
        getvals=parsed_path.query.split('&')
        self.get_vals={}
        print "GET",self.path

        try:
            for s in getvals:
                if s.find('=')!=-1:
                    (key,val) = s.split('=')
                    self.get_vals[key] = val
        except:
            print "error get!"
            self.get_vals={}
                
        self.currule=RULE_NO
        self.idreg=0

        if self.path.find(".html")!=-1:
            self._send_HEAD("text/html",404)
            return
        if self.path.find(".woff")!=-1:
            self._send_HEAD("application/x-font-woff",200)
            message=self.get_file(self.path)
            self._write(message)
            return
        if self.path.find(".js")!=-1:
            self._send_HEAD("text/javascript",200)
            message=self.get_file(self.path)
            self._write(message)
            return
        if self.path.find(".css")!=-1:
            self._send_HEAD("text/css",200)
            message=self.get_file(self.path)
            self._write(message)
            return

        #print "mysql open ..."
        if not self.mysql_open():
            self._send_HEAD("text/html",404)
            return
        else:
            self.db._read_sets()
        #print "mysql opened!"

        if self.path=='/login':
            self.iduser=0
            self.curlogin=""
            self.currule=RULE_NO
            self.wbody("/login.html")
            return

        #print "Authorize ..."
        if not self.ReadCookie():
            if not self.GetAuth(self.get_vals):
                self._redirect("/login")
                return

        self.GetAuth(self.get_vals)

        if not self.verify():
            self._redirect("/login")
            return

        if (self.path.find("/unlogin")==0):
            self._send_redirect("/login")
            self.ClearCookie()
            self.end_headers()
            return
        #print "Authorized!"

        """ GET SIMPLE REQUEST
            ------------------
        """    
        if self.path=='/':
            self.wbody("/index.html")
            return

        if self.path=='/service':
            self._request("","/service.html","/")
            return

        if self.path=='/ot':
            self._request(RULE_ADM,"/ot.html","/")
            return

        if self.path=='/ot/check':
            self._request(RULE_ADM,"/otcheck.html","/")
            return

        """ GET REGS
            ------------------
        """ 


        if parsed_path.path=='/reg':
            if self.currule!=RULE_SYS:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._regs_get(id=int(self.get_vals['id'])):
                self.db.reg=self.db.tb_regs._clear()
            html=self.pattern_rep_hash(self.get_file("/ed_reg.html"),self.db.reg)
            self.whtml(html)
            return

        if self.path=='/regs':
            if self.currule!=RULE_SYS:
                self._redirect("/")
                return
            regs=self.db._regs_gets()
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[0,1,4],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"reg"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if self.path=='/kasses':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            regs=self.db._kasses_gets_html(self.idreg)
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[1,3,5,6,8,12,13,15,16,17,18,19],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"kassa"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if parsed_path.path=='/kassa':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._kasses_get(self.idreg,int(self.get_vals['id'])):
                self.db.kassa=self.db.tb_kasses._clear()
                self.db.kassa['idreg']=self.idreg
            prices=self.db._prices_gets(self.idreg)
            sel=ht_db2select(prices,0,2,self.db.kassa['idprice'])
            html=self.pattern_rep_hash(self.get_file("/ed_kassa.html"),self.db.kassa)
            html=self.pattern_rep_arr(html,["%select_price%"],[sel])
            self.whtml(html)
            return

        if self.path=='/prices':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            regs=self.db._prices_gets(self.idreg)
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[2,3,4],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"price"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if parsed_path.path=='/price':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._prices_get(self.idreg,int(self.get_vals['id'])):
                self.db.price=self.db.tb_prices._clear()
                self.db.price['idreg']=self.idreg
            html=self.pattern_rep_hash(self.get_file("/ed_price.html"),self.db.price)
            self.whtml(html)
            return

        if self.path=='/gplaces':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            regs=self.db._gplace_gets(self.idreg)
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[0,1,2],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"gplace"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if parsed_path.path=='/gplace':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._gplace_get(self.idreg,int(self.get_vals['id'])):
                self.db.gplace=self.db.tb_gplace_hd._clear()
                self.db.gplace['idreg']=self.idreg
            html=self.pattern_rep_hash(self.get_file("/ed_gplace.html"),self.db.gplace)
            self.whtml(html)
            return

        if parsed_path.path=='/gplace_ct':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            self.db._gplace_get(self.idreg,int(self.get_vals['id']))
            places=self.db._places_gets(self.idreg)
            d=[]
            for p in places:
                find=False
                for g in self.db.gplace_ct:
                    if g[2]==p[1]:
                        find=True
                        break
                if find:
                    d.append([1,p[1],p[6],p[5],str(g[3]),str(g[4])])
                else:
                    d.append([0,p[1],p[6],p[5],'',''])
            j=json.dumps(d,ensure_ascii=False)
            self.wjson(j)
            return

        if self.path=='/tlists':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            regs=self.db._tlist_gets(self.idreg)
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[0,1,3],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"tlist"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if parsed_path.path=='/tlist':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._tlist_get(self.idreg,int(self.get_vals['id'])):
                self.db.tlist=self.db.tb_gplace_hd._clear()
                self.db.tlist['idreg']=self.idreg
                self.db.tlist['idprice']=1
            prices=self.db._prices_gets(self.idreg)
            sel=ht_db2select(prices,0,2,self.db.tlist['idprice'])
            html=self.pattern_rep_hash(self.get_file("/ed_tlist.html"),self.db.tlist)
            html=self.pattern_rep_arr(html,["%select_price%"],[sel])
            self.whtml(html)
            return

        if parsed_path.path=='/tlist_ct':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            self.db._tlist_get(self.idreg,int(self.get_vals['id']))
            d={}
            for t in self.db.tlist_ct:
                d[t[0]]=t[1]
            j=json.dumps(d,ensure_ascii=False)
            self.wjson(j)
            return

        if self.path=='/actions':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            regs=self.db._actions_gets(self.idreg)
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[0,2,4,5,3],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"action"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if parsed_path.path=='/action':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._actions_get(self.idreg,int(self.get_vals['id'])):
                self.db.action=self.db.tb_actions_hd._clear()
                self.db.action['idreg']=self.idreg
                self.db.action['daysweek']="1111111";
            html=self.pattern_rep_hash(self.get_file("/ed_action.html"),self.db.action)
            self.whtml(html)
            return

        if parsed_path.path=='/regs_sets':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            regs=self.db._regs_sets_gets(self.idreg)
            html=self.get_file("/regs.html")
            params=self.pattern_params_get(html)
            htable = ht_db2table(regs,[0,2,3],0,gethash(params,'table',""))
            html=self.pattern_rep_arr(html,["%table%","%n%"],[htable,"regs_set"])
            html=self.pattern_params_clear(html)
            self.write_body(html)
            return

        if parsed_path.path=='/regs_set':
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if not self.get_vals.has_key('id'):
                self._redirect("/")
                return
            if not self.db._regs_sets_get(self.idreg,int(self.get_vals['id'])):
                self.db.regs_set=self.db.tb_regs_sets._clear()
                self.db.regs_set['idreg']=self.idreg
            html=self.pattern_rep_hash(self.get_file("/ed_regs_set.html"),self.db.regs_set)
            self.whtml(html)
            return

        """ GET PRICE
            ------------------
        """ 
        if parsed_path.path=='/get_price':
            if not self.get_vals.has_key('parent'):
                self._write(POST_FALSE)
                return
            if not self.get_vals.has_key('idprice'):
                self._write(POST_FALSE)
                return
            parent=self.get_vals['parent']
            idprice=self.get_vals['idprice']
            if not self.db._price_get_group(self.idreg,int(idprice),parent):
                self.db._price_get_group(self.idreg,int(idprice),"0")
            j=json.dumps(self.db.price,ensure_ascii=False)
            self.wjson(j)
            return

        """ GET MY PRICE
            ------------------
        """ 

        if parsed_path.path=='/cmd/myprice':
            #print "myprice",int(self.get_vals['idplace']),int(self.get_vals['nkassa'])
            if not self.verify_icecash():
                self._write(POST_FALSE)
                print "failed query"
                return
            self.create_icecash(self.db,self.curlogin,int(self.get_vals['idplace']),int(self.get_vals['nkassa']))
            if not self.icecash.verify():
                print "failed verify"
                print self.db,self.curlogin,int(self.get_vals['idplace']),int(self.get_vals['nkassa'])
                self._write(POST_FALSE)
                return
            if not self.icecash.get_price():
                #print "failed getprice"
                self._write(POST_FALSE)
                return
            self._write(self.db.price['name'])
            del self.icecash
            return

        if parsed_path.path=='/cmd/myprice/set':
            if not self.verify_icecash():
                self._write(POST_FALSE)
                print "failed query"
                return
            self.create_icecash(self.db,self.curlogin,int(self.get_vals['idplace']),int(self.get_vals['nkassa']))
            if not self.icecash.verify():
                self._write(POST_FALSE)
                return
            if not self.icecash.set_price():
                self._write(POST_FALSE)
                return
            self._write(POST_TRUE)
            self.icecash.time_update()
            del self.icecash
            return

        """ GET ACTIONS """
        if parsed_path.path=="/cmd/curaction":
            self.db._regs_get(regid=self.curlogin)
            self._write(str(self.db.reg['action']))
            return

        if parsed_path.path=="/cmd/actions":
            self.db._regs_get(regid=self.curlogin)
            curaction=int(self._getval('curaction',0))
            idplace=int(self._getval('idplace',0))
            if curaction==self.db.reg['action']:
                j=json.dumps({'id':self.db.reg['action'],'actions':[]},ensure_ascii=False)
                self._write(j)
                return
            self.create_actions(self.idreg,self.db)
            self.actions._read()
            if self.actions._filter_place(idplace):
                j=json.dumps({'id':self.db.reg['action'],'actions':self.actions.f_actions,'tlists':self.actions.tlists},ensure_ascii=False)
            else:
                j=json.dumps({'id':self.db.reg['action'],'actions':[],'tlist':[]},ensure_ascii=False)
            self._write(j)
            return

        """ GET REGS SETS """
        if parsed_path.path=="/cmd/cursets":
            self.db._regs_get(regid=self.curlogin)
            self._write(str(self.db.reg['sets']))
            return

        if parsed_path.path=='/cmd/regs_sets':
            self.db._regs_get(regid=self.curlogin)
            cursets=int(self._getval('cursets',0))
            if cursets==self.db.reg['sets']:
                j=json.dumps({'id':self.db.reg['sets'],'sets':[]},ensure_ascii=False)
                self.wjson(j)
                return
            sets = self.db._regs_sets_gets(self.db.idreg)
            _sets={}
            for s in sets:
                _sets[s[2]]=s[3]
            j=json.dumps({'id':self.db.reg['sets'],'sets':_sets},ensure_ascii=False)
            self.wjson(j)
            return

        """ GET ZET FOR 1C """

        if parsed_path.path=="/getup/Zet/list":
            dt1=self._getval('dt1',None)
            dt2=self._getval('dt2',None)
            up=int(self._getval('up',0))
            xml=self._getval('xml',None)

            self.db._regs_get(regid=self.curlogin)
            self.db._Zet_gets(self.db.idreg,dt1,dt2,up=up)
            if xml==None:
                j=json.dumps(self.db.Zets,ensure_ascii=False)
                self.wjson(j)
            else:
                body=""
                for hline in self.db.Zets:
                    sline=""
                    for k,v in hline.items():
                        sline+="\t<%s>%s</%s>\n" % (k,v,k)
                    x="\t<zet>\n%s</zet>\n\n" % (sline)
                    body+=x
                XML='<?xml version="1.0" encoding="UTF-8"?>\n<data type="icecash_zets">\n\n<body>\n'+body+'</body>\n\n</data>'
                self.wxml(XML)
            return

        if parsed_path.path=="/getup/Zet/get":
            id=int(self._getval('id',0))
            if id==0:
                self._send_false()
                return
            idplace=int(self._getval('idplace',1))
            nkassa=int(self._getval('nkassa',1))
            xml=self._getval('xml',None)
            self.db._regs_get(regid=self.curlogin)
            if not self.db._Zet_get(self.db.idreg,idplace,nkassa,id):
                self._write(POST_FALSE)
                return
            if xml==None:
                j=json.dumps({'head':self.db.Zet,'body':self.db.Zet_ct},ensure_ascii=False)
                self.wjson(j)
            else:
                head=""
                for k,v in self.db.Zet.items():
                    head+="\t<%s>%s</%s>\n" % (k,v,k)
                body=""
                for hline in self.db.Zet_ct:
                    sline=""
                    for k,v in hline.items():
                        sline+="\t<%s>%s</%s>\n" % (k,v,k)
                    body+="\t<tov>\n%s</tov>\n\n" % (sline)
                XML='<?xml version="1.0" encoding="UTF-8"?>\n<data type="icecash_zet">\n\n<head>\n'+head+'</head>\n\n<body>\n'+body+'</body>\n\n</data>'
                self.wxml(XML)
                body=""
            return

        if parsed_path.path=="/getup/Zet/set":
            up=int(self._getval('up',1))
            id=int(self._getval('id',0))
            idplace=int(self._getval('idplace',1))
            nkassa=int(self._getval('nkassa',1))
            if id==0:
                self._write(POST_FALSE)
                return
            self.db._regs_get(regid=self.curlogin)
            if not self.db._Zet_upd(self.db.idreg,idplace,nkassa,id,{'up':up}):
                self._send_false()
            else:
                self._send_true()
            return

        if parsed_path.path=="/ot/check":
            self.db._regs_get(regid=self.curlogin)
            id=self._getval('id',None)
            idplace=self._getval('idplace',None)
            nkassa=self._getval('nkassa',None)
            if id:
                if not self.db._trsc_get_check(int(idplace),int(nkassa),int(id)):
                    self._write(POST_FALSE)
                else:
                    j=json.dumps({'hd':self.db.trsc_hd,'ct':self.db.trsc_ct},ensure_ascii=False)
                    self.wjson(j)
                    return

            dt1=self._getval('dt1',None)
            dt2=self._getval('dt2',None)
            tm1=self._getval('tm1',None)
            tm2=self._getval('tm2',None)
            ncheck=self._getval('ncheck',None)
            tcheck=self._getval('tcheck',None)
            tpay=self._getval('tpay',None)
            tclose=self._getval('tclose',None)
            dcard=self._getval('dcard',None)
            bcard=self._getval('bcard',None)
            fiscal=self._getval('fiscal',None)
            error=self._getval('error',None)
            discount=self._getval('discount',None)
            bonus=self._getval('bonus',None)
            summa=self._getval('summa',None)
            alco=self._getval('alco',None)
            code=self._getval('code',None)
            group=self._getval('idgroup',None)
            
            self.db._trsc_filter(int(idplace),int(nkassa),dt1,dt2,tm1,tm2,ncheck,tcheck,tpay,tclose,dcard,bcard,fiscal,error,discount,bonus,summa,alco,code,group)
            j=json.dumps(self.db.f_checks,ensure_ascii=False)
            self.wjson(j)
            return

        """ GET FILES REQUEST
            ------------------
        """ 
        if self.path.find('/files/')!=-1:
            fn=parsed_path.path
            if not os.path.isfile("site"+fn):
                self.send_response(404)
                self.end_headers()
                return
            self.write_file(fn)
            return

        if self.path.find('/fo/ls')!=-1:
            if self.currule!=RULE_ADM and self.currule!=RULE_SYS:
                self._write(POST_FALSE)
                return
            if not self.get_vals.has_key('path'):
                self._write(POST_FALSE)
                return
            path=self.get_vals['path'].replace("..","")
            d=lsdir('site/files/'+path)

            d.append(path)
            xml=""
            if self.get_vals.has_key('json'):
                JSON=json.dumps(d,ensure_ascii=False)
                self.wjson(JSON)
            else:
                dirs,files,cur=d
                dirs.sort()
                files.sort()
                xml+="\t<cur>"+cur+"</cur>\n"
                for k in dirs:
                    fname=k.decode("utf8")
                    x="\t<dir>"+fname+"</dir>\n"
                    xml+=x
                for k in files:
                    fname=k.decode("utf8")
                    x="\t<file>"+fname+"</file>\n"
                    xml+=x
                XML='<?xml version="1.0" encoding="UTF-8"?>\n<data type="icecash_uplist">\n\n<body>\n'+xml+"</body>\n\n</data>"
                self.wxml(XML)
            return

        if self.path.find('/fo/rm')!=-1:
            if self.currule!=RULE_SYS:
                self._write(POST_FALSE)
                return
            if not self.get_vals.has_key('path'):
                self._write(POST_FALSE)
                return
            path=self.get_vals['path'].replace("..","")
            fn='site/files/'+path
            try:
                os.remove(fn)
                self._write(POST_TRUE)
            except:
                self._write(POST_FALSE)
            return

    """ POST REQUEST 
        ------------
    """    
    
    def do_POST(self):
        self.cur_css='blue.css'
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        
        if not self.mysql_open():
            self._send_HEAD("text/html",404)
            print "error. not open mysql"
            return
        else:
            self.db._read_sets()

        if (self.path.find("/login")==0):
            self._send_redirect("/")
            self.WriteCookie(form)
            self.end_headers()
            return

        if not self.ReadCookie():
            if not self.PostAuth(form):
                self._redirect("/login")
                return

        self.PostAuth(form)

        if not self.verify():
            print "not verify"
            self._redirect("/login")
            return

        if self.path=="/reg":
            if self.currule!=RULE_SYS:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_regs._add_post(form))
                    else:
                        self.db.run(self.db.tb_regs._upd_post(int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_regs._del(int(form['id'].value)))
            self._send_redirect("/regs")
            self.end_headers()
            return

        if self.path=="/kassa":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_kasses._add_post(form))
                    else:
                        self.db.run(self.db.tb_kasses._upd_post(self.idreg,int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_kasses._del(self.idreg,int(form['id'].value)))
            self._send_redirect("/kasses")
            self.end_headers()
            return

        if self.path=="/price":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_prices._add_post(form))
                    else:
                        self.db.run(self.db.tb_prices._upd_post(self.idreg,int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_prices._del(self.idreg,int(form['id'].value)))
            self._send_redirect("/prices")
            self.end_headers()
            return

        if self.path=="/gplace":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_gplace_hd._add_post(form))
                    else:
                        self.db.run(self.db.tb_gplace_hd._upd_post(self.idreg,int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_gplace_hd._del(self.idreg,int(form['id'].value)))
            self.db._inc_action(self.idreg)
            self._send_redirect("/gplaces")
            self.end_headers()
            return

        if self.path=="/regs_set":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_regs_sets._add_post(form))
                    else:
                        self.db.run(self.db.tb_regs_sets._upd_post(self.idreg,int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_regs_sets._del(self.idreg,int(form['id'].value)))
            self.db._inc_sets(self.idreg)
            self._send_redirect("/regs_sets")
            self.end_headers()
            return

        if self.path=="/tlist":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_tlist_hd._add_post(form))
                    else:
                        self.db.run(self.db.tb_tlist_hd._upd_post(self.idreg,int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_tlist_hd._del(self.idreg,int(form['id'].value)))
            self.db._inc_action(self.idreg)
            self._send_redirect("/tlists")
            self.end_headers()
            return

        if self.path=="/action":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("save"):
                    if int(form['id'].value)==0:
                        self.db.run(self.db.tb_actions_hd._add_post(form))
                    else:
                        self.db.run(self.db.tb_actions_hd._upd_post(self.idreg,int(form['id'].value),form))
                if form.has_key("delete"):
                    self.db.run(self.db.tb_actions_hd._del(self.idreg,int(form['id'].value)))
            self.db._inc_action(self.idreg)
            self._send_redirect("/actions")
            self.end_headers()
            return

        if self.path=="/gplace_ct":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("gplaces"):
                    j=json.loads(form['gplaces'].value)
                    self.db.run(self.db.tb_gplace_ct._del(self.idreg,int(form['id'].value)))
                    for (k,v) in j.items():
                        if str(v)=='1':
                            self.db.run(self.db.tb_gplace_ct._add(self.idreg,int(form['id'].value),k))
            self.db._inc_action(self.idreg)
            self._send_redirect("/gplaces")
            self.end_headers()
            return

        if self.path=="/tlist_ct":
            if self.currule!=RULE_SYS and self.currule!=RULE_ADM:
                self._redirect("/")
                return
            if form.has_key("id"):
                if form.has_key("sprice"):
                    j=json.loads(form['sprice'].value)
                    self.db.run(self.db.tb_tlist_ct._del(self.idreg,int(form['id'].value)))
                    for (k,v) in j.items():
                        self.db.run(self.db.tb_tlist_ct._add(self.idreg,int(form['id'].value),k))
            self.db._inc_action(self.idreg)
            self._send_redirect("/tlists")
            self.end_headers()
            return

        """ POST FILES REQUEST
            ----------------
        """    
        if (self.path.find("/files")==0):
            if self.currule!=RULE_ADM and self.currule!=RULE_SYS:
                self._send_false()
                return
            content_len = int(self.headers.getheader('content-length', 0))
            if form.has_key("file"): 
                fn=os.path.basename(form['file'].filename)
                file_data=form['file'].file.read()
                path=self.path.replace("..","")
                p=path+"/"+fn
                f=os.path.basename(p)
                d=os.path.dirname(p)
                print d,f
                if self.put_file(file_data,path+"/"+fn):
                    if d=='/files/download/price':
                        if not self.upload_price(f):
                            self._send_false()
                            return
                    self._send_true()
                else:
                    print "FALSE"
                    self._send_false()
                del file_data
            else:
                self._send_false()
            print 'get data',content_len
            return

        if self.path=='/cmd/regs_sets':
            if not form.has_key('sets'):
                self._write(POST_FALSE)
                return
            sets=json.loads(form['sets'].value)
            self.db._regs_get(self.curlogin)
            for k,v in sets.items():
                self.db.run(self.db.tb_regs_sets._upd_name(self.db.idreg,k,{'value':str(v)}))
            self.db._inc_sets(self.idreg)
            self._write(POST_TRUE)
            return

        if self.path=='/cmd/trsc/send':
            if form.has_key('version'):
                version=form['version'].value
            else:
                version="0"
            if form.has_key('upgrade'):
                upgrade=form['upgrade'].value
            else:
                upgrade="0"
            if form.has_key('prn_name'):
                prn_name=form['prn_name'].value
            else:
                prn_name="-"
            if form.has_key('prn_type'):
                prn_type=form['prn_type'].value
            else:
                prn_type="-"

            ip=self.client_address[0]
            if not self.verify_icecash_post(form):
                print "error idplace nkassa"
                self._write(POST_FALSE)
                return
            self.create_icecash(self.db,self.curlogin,int(form['idplace'].value),int(form['nkassa'].value))
            #print "recieve data from:",ip,version,upgrade,prn_name,prn_type
            if not self.icecash.verify():
                print "error verify"
                self._write(POST_FALSE)
                return
            self.icecash.time_update({'version':version,'upgrade':upgrade,'prn_name':prn_name,'prn_type':prn_type,'ip':ip})
            if not form.has_key('data'):
                self._write(POST_FALSE)
                return
            #self.icecash.time_update(version=version,upgrade=upgrade,prn_name=prn_name,prn_type=prn_type,ip=ip)
            d=json.loads(form['data'].value)
            ups=self.icecash.trsc_add(d)
            j=json.dumps(ups,ensure_ascii=False)
            self.wjson(j)
            del self.icecash
            return

        if self.path=='/cmd/Zet/send':
            if not form.has_key('data'):
                self._write(POST_FALSE)
                return
            if not self.verify_icecash_post(form):
                self._write(POST_FALSE)
                print "failed query"
                return
            self.create_icecash(self.db,self.curlogin,int(form['idplace'].value),int(form['nkassa'].value))
            if not self.icecash.verify():
                self._write(POST_FALSE)
                return
            self.icecash.time_update()
            d=json.loads(form['data'].value)
            ups=self.icecash.Zet_add(d)
            j=json.dumps(ups,ensure_ascii=False)
            self.wjson(j)
            del self.icecash
            return

        self.send_response(200)
        self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Создаем веб сервер многопоточный """

if __name__ == '__main__':
    db = dbIceServ.dbIceServ(dbIceServ.DATABASE, MYSQL_HOST, dbIceServ.MYSQL_USER, dbIceServ.MYSQL_PASSWORD) 
    if db.open():
        pass
    else:
        print "DTPWeb Server down. Database not exist"
        sys.exit(1)

    db._read_sets()
    ice_create_lock()
    #TEMPORARY TEST CHANCGE
    #db.sets['server_port']=10101
    server = ThreadedHTTPServer(('', int(db.sets['server_port'])), Handler)
    print 'Start dIceServ Server v %s [%s]' % (VERSION,db.sets['server_port'])
    db.close()
    
    server.serve_forever()


