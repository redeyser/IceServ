#!/usr/bin/python
# -*- coding: utf-8
# version 2.000
# DataBase for IceCash
import my
import os
import re
from md5 import md5
import tbIceServ as tbs
import datetime

DATABASE = "IceServ"
MYSQL_USER = "iceserv"
MYSQL_PASSWORD = "iceserv1024"

def _round(V,n):
    z=str(V.__format__(".4f")).split(".")
    if len(z)<2:
        return str(V)
    else:
        d=int(z[0])
        f=z[1].ljust(n,"0")
    l=len(f)
    a=[]
    for i in range(l):
        a.append(int(f[i]))
    r=range(l)[n:]
    r.reverse()
    x=range(l)[:n]
    x.reverse()
    ost=0
    for i in r:
        a[i]+=ost
        if a[i]>=5:
            ost=1
        else:
            ost=0
    for i in x:
        a[i]+=ost
        if a[i]>9:
            a[i]=0
            ost=1
        else:
            ost=0
            break
    d+=ost
    s=""
    for i in range(n):
        s+=str(a[i])
    if n>0:
        s="."+s
    result=str(d)+s
    return result

def Str2Shash(s,c,eq):
    a = s.split(c)
    Sarr=[]
    for e in a:
        Sarr.append(e.strip(" "))
    Shash={}
    for e in Sarr:
        if e.find(eq)!=-1:
            a=e.split(eq)
            Shash[a[0].strip(" ")] = a[1].strip(" ")
        else:
            Shash[e.strip(" ")] = e.strip(" ")
    return Shash

def array4json(a):
    r=[]
    for h in a:
        if type(h)==datetime.timedelta or type(h)==datetime.date:
            r.append(str(h))
        else:
            r.append(h)
    return r

class dbIceServ(my.db):
    def __init__(self,dbname,host,user,password):
        my.db.__init__(self,dbname,host,user,password)
        self.tb_sets        = tbs.tb_sets       ('tb_sets')
        self.tb_regs        = tbs.tb_regs       ('tb_regs')
        self.tb_kasses      = tbs.tb_kasses     ('tb_kasses')
        self.tb_prices      = tbs.tb_prices     ('tb_prices')
        self.tb_price       = tbs.tb_price      ('tb_price')
        self.tb_price_shk   = tbs.tb_price_shk  ('tb_price_shk')
        self.tb_discount    = tbs.tb_discount   ('tb_discount')
        self.tb_trsc_hd     = tbs.tb_trsc_hd    ('tb_trsc_hd')
        self.tb_trsc_ct     = tbs.tb_trsc_ct    ('tb_trsc_ct')
        self.tb_types       = tbs.tb_types      ('tb_types')
        self.tb_Zet         = tbs.tb_Zet        ('tb_Zet')
        self.tb_Zet_cont    = tbs.tb_Zet_cont   ('tb_Zet_cont')
        self.tb_gplace_hd   = tbs.tb_gplace_hd  ('tb_gplace_hd')
        self.tb_gplace_ct   = tbs.tb_gplace_ct  ('tb_gplace_ct')
        self.tb_tlist_hd    = tbs.tb_tlist_hd   ('tb_tlist_hd')
        self.tb_tlist_ct    = tbs.tb_tlist_ct   ('tb_tlist_ct')
        self.tb_actions_hd  = tbs.tb_actions_hd ('tb_actions_hd')
        self.tb_regs_sets   = tbs.tb_regs_sets  ('tb_regs_sets')

        self.reg=None

    def _inc_action(self,idreg):
        self.run(self.tb_regs._inc_action(idreg))

    def _inc_sets(self,idreg):
        self.run(self.tb_regs._inc_sets(idreg))

    def _price_get(self,idreg,idprice,code):
        price=self.get(self.tb_price._get(idreg,idprice,code))
        if len(price)==0:
            return False
        else:
            self.price=self.tb_price.result2values(price[0])
            return True

    def _price_get_group(self,idreg,idprice,parent):
        if parent=="":
            parent="0"
        self.price=self.get(self.tb_price._get_group(idreg,idprice,parent))
        if len(self.price)==0:
            return False
        else:
            return True

    def _prices_find(self,regid,name):
        price=self.get(self.tb_prices._find(regid,name))
        if len(price)==0:
            return False
        else:
            price=self.tb_prices.result2values(price[0])
            self.price=price
            return True

    def _prices_gets(self,idreg):
        return self.get(self.tb_prices._gets(idreg))

    def _prices_get(self,idreg,id):
        price=self.get(self.tb_prices._get(idreg,id))
        if len(price)==0:
            return False
        else:
            price=self.tb_prices.result2values(price[0])
            self.price=price
            return True

    def _prices_upd(self,idreg,id,struct):
        self.run(self.tb_prices._upd(idreg,id,struct))

    def _places_gets(self,idreg):
        return self.get(self.tb_kasses._get_places(idreg))

    def _kasses_gets(self,idreg):
        return self.get(self.tb_kasses._gets(idreg))

    def _kasses_gets_html(self,idreg):
        return self.get(self.tb_kasses._gets_html(idreg))

    def _kasses_get(self,idreg,id):
        kassa=self.get(self.tb_kasses._get(idreg,id))
        if len(kassa)==0:
            return False
        else:
            kassa=self.tb_kasses.result2values(kassa[0])
            self.kassa=kassa
            return True

    def _kasses_find(self,idreg,idplace,nkassa):
        kassa=self.get(self.tb_kasses._find(idreg,idplace,nkassa))
        if len(kassa)==0:
            return False
        else:
            kassa=self.tb_kasses.result2values(kassa[0])
            self.kassa=kassa
            return True

    def _kasses_upd(self,idreg,id,struct):
        self.run(self.tb_kasses._upd(idreg,id,struct))

    def _gplace_gets(self,idreg):
        return self.get(self.tb_gplace_hd._gets(idreg))


    def _gplace_get(self,idreg,id):
        d=self.get(self.tb_gplace_hd._get(idreg,id))
        if len(d)==0:
            return False
        else:
            d=self.tb_gplace_hd.result2values(d[0])
            self.gplace=d
            d=self.get(self.tb_gplace_ct._gets(idreg,id))
            self.gplace_ct=d
            return True

    def _tlist_gets(self,idreg):
        return self.get(self.tb_tlist_hd._gets(idreg))

    def _tlist_get(self,idreg,id):
        d=self.get(self.tb_tlist_hd._get(idreg,id))
        if len(d)==0:
            return False
        else:
            d=self.tb_tlist_hd.result2values(d[0])
            self.tlist=d
            d=self.get(self.tb_tlist_ct._gets(idreg,id))
            self.tlist_ct=d
            return True

    def _actions_gets(self,idreg):
        return self.get(self.tb_actions_hd._gets(idreg))

    def _actions_get(self,idreg,id):
        d=self.get(self.tb_actions_hd._get(idreg,id))
        if len(d)==0:
            return False
        else:
            d=self.tb_actions_hd.result2values(d[0])
            self.action=d
            return True

    def _regs_sets_gets(self,idreg):
        return self.get(self.tb_regs_sets._gets(idreg))

    def _regs_sets_get(self,idreg,id):
        d=self.get(self.tb_regs_sets._get(idreg,id))
        if len(d)==0:
            return False
        else:
            d=self.tb_regs_sets.result2values(d[0])
            self.regs_set=d
            return True

    def _regs_gets(self):
        return self.get(self.tb_regs._gets())

    def _regs_add(self,aval):
        self.run(self.tb_regs._add(aval))

    def _regs_upd(self,idreg,aval):
        self.run(self.tb_regs._upd(idreg,aval))

    def _regs_get(self,regid="",id=0):
        reg=self.get(self.tb_regs._get(regid=regid,id=id))
        if len(reg)==0:
            return False
        else:
            reg=self.tb_regs.result2values(reg[0])
            self.reg=reg
            self.idreg=int(self.reg['id'])
            return True

    def _regs_auth(self,login,password):

        reg=self.get(self.tb_regs._get(regid=login))
        if len(reg)==0:
            self.reg=None
            return False
        else:
            reg=self.tb_regs.result2values(reg[0])
            self.reg=reg
            if md5(password).hexdigest()==reg['adm_pass']:
                if reg['regid']=='sys':
                    self.rule='sys'
                else:
                    self.rule='adm'
                return True
            else:
                if md5(password).hexdigest()==reg['client_pass']:
                    self.rule='cnt'
                    return True
                else:
                    return False

    def _read_sets(self,group=''):
        self.sets={}
        data = self.get(self.tb_sets._getall(group))
        for d in data:
            self.sets[d[2]]=d[3]
        try:
            self.idplace=int(self.sets['idplace'])
            self.nkassa=int(self.sets['nkassa'])
        except:
            self.idpalce=1
            self.nkassa=1

    def _sets_get(self,group=''):
        sets={}
        data = self.get(self.tb_sets._getall(group))
        for d in data:
            sets[d[2]]=d[3]
        return sets

    def _sets_add(self,g,n,v):
        self.run(self.tb_sets._add([g,n,v]))

    def _sets_upd(self,n,v):
        self.run(self.tb_sets._upd(n,v))

    def _Zet_find(self,idreg,idplace,nkassa,dt,id):
        Zet=self.get(self.tb_Zet._find(idreg,idplace,nkassa,dt,id))
        if len(Zet)>0:
            self.Zet=self.tb_Zet.result2values(Zet[0],tostr=True)
            return True
        else:
            return False

    def _Zet_gets(self,idreg=1,dt1=None,dt2=None,up=None):
        self.Zets=self.get(self.tb_Zet._gets(idreg,dt1,dt2,up))
        if len(self.Zets)==0:
            return False
        Zets=[]
        for v in self.Zets:
            struct=self.tb_Zet.result2values(v,tostr=True)
            Zets.append(struct)
        self.Zets=Zets
        return True

    def _Zet_get(self,idreg,idplace,nkassa,id):
        self.Zet=self.get(self.tb_Zet._get(idreg,idplace,nkassa,id))
        if len(self.Zet)==0:
            return False
        else:
            self.Zet=self.tb_Zet.result2values(self.Zet[0],tostr=True)
        Zet_ct=self.get(self.tb_Zet_cont._get(idreg,idplace,nkassa,id))
        self.Zet_ct=[]
        for n in Zet_ct:
            self.Zet_ct.append(self.tb_Zet_cont.result2values(n,tostr=True))
        return True

    def _Zet_upd(self,idreg,idplace,nkassa,id,struct):
        return self.run(self.tb_Zet._upd(idreg,idplace,nkassa,id,struct))

    def _Zet_add(self,hd,cts,withouthd=False):
        if not withouthd:
            if not self.run(self.tb_Zet._add(hd)):
                return False
            idhd = self.get(my.Q_LASTID)[0][0]
        else:
            idhd=hd['id']
        summa=0
        for ct in cts:
            ct['idhd']      = idhd
            ct['idreg']     = hd['idreg']
            ct['idplace']   = hd['idplace']
            ct['nkassa']    = hd['nkassa']
            summa+=float(ct['paramf3'])
            if not self.run(self.tb_Zet_cont._add(ct)):
                self.run(self.tb_Zet._del(hd['idreg'],hd['idplace'],hd['nkassa'],idhd))
                self.run(self.tb_Zet_cont._del(hd['idreg'],hd['idplace'],hd['nkassa'],idhd))
                return False
        if _round(summa,2)!=_round(float(hd['summa']),2):
            print "ERROR SUMMACT<>SUMMAHD!"
            print summa,hd['summa']
            return False

        return True
                
    def _trsc_find(self,idreg,idplace,nkassa,dt,tm,id):
        t=self.get(self.tb_trsc_hd._find(idreg,idplace,nkassa,dt,tm,id))
        if len(t)>0:
            return True
        else:
            return False

    def _trsc_add(self,hd,cts):
        if not self.run(self.tb_trsc_hd._add(hd)):
            return False
        idhd = self.get(my.Q_LASTID)[0][0]
        for ct in cts:
            ct[1]=idhd
            ct.insert(1,hd[0])
            ct.insert(2,hd[1])
            ct.insert(3,hd[2])
            if not self.run(self.tb_trsc_ct._add(ct)):
                self.run(self.tb_trsc_hd._del(hd[0],hd[1],hd[2],idhd))
                self.run(self.tb_trsc_ct._del(hd[0],hd[1],hd[2],idhd))
                return False
        return True

    def _trsc_get_check(self,idplace,nkassa,id,tostr=True):
        trsc_hd=self.get(self.tb_trsc_hd._get_check(self.idreg,idplace,nkassa,id))
        if len(trsc_hd)==0:
            return False
        self.trsc_hd = self.tb_trsc_hd.result2values(trsc_hd[0],tostr=tostr)
        trsc_ct=self.get(self.tb_trsc_ct._get_title(self.idreg,idplace,nkassa,id))
        self.trsc_ct=[]
        for c in trsc_ct:
            d=self.tb_trsc_ct.result2values(c,tostr=tostr)
            d['name']=c[-1]
            self.trsc_ct.append(d)
        return True

    def _trsc_filter(self,idplace,nkassa,dt1,dt2,tm1,tm2,ncheck,tcheck,tpay,tclose,dcard,bcard,fiscal,error,discount,bonus,summa,alco,code,group):
        r=self.get(self.tb_trsc_hd._filter(self.idreg,idplace,nkassa,dt1,dt2,tm1,tm2,ncheck,tcheck,tpay,tclose,dcard,bcard,fiscal,error,discount,bonus,summa,alco,code,group))
        self.f_checks=[]
        for n in r:
            data=self.tb_trsc_hd.result2values(n,tostr=True)
            data['vir']=float(data['summa'])-float(data['discount_sum'])-float(data['bonus_discount'])
            self.f_checks.append(data)

    def _create(self):
        if self.open():
            self.run("drop user '%s'@'localhost'" % MYSQL_USER)
            self.run("drop database %s" % DATABASE)
            self.run("create database %s" % DATABASE)
            self.run("create user '%s'@'localhost' IDENTIFIED BY '%s'" % (MYSQL_USER,MYSQL_PASSWORD))
            self.run("grant all on "+DATABASE+".* to '%s'@'localhost'" % MYSQL_USER)
            self.run("flush privileges")
            self.run("use %s" % DATABASE)

            self.run(self.tb_sets._create())
            self._sets_add('server','version','2.0')
            self._sets_add('server','server_port','10100')
            self._sets_add('server','adm_pass',md5("iceserv1024").hexdigest())

            self._sets_add('client','timeout_ping','15')
            self._sets_add('client','timeout_query','60')

            self.run(self.tb_trsc_hd._create())
            self.run(self.tb_trsc_ct._create())
            self.run(self.tb_prices._create())
            self.run(self.tb_price._create())
            self.run(self.tb_price_shk._create())
            self.run(self.tb_discount._create())
            self.run(self.tb_regs._create())
            self.run(self.tb_kasses._create())
            self.run(self.tb_types._create())
            self.run(self.tb_Zet._create())
            self.run(self.tb_Zet_cont._create())
            self.run(self.tb_gplace_hd._create())
            self.run(self.tb_gplace_ct._create())
            self.run(self.tb_tlist_hd._create())
            self.run(self.tb_tlist_ct._create())
            self.run(self.tb_actions_hd._create())
            self.run(self.tb_regs_sets._create())

            self._regs_add(['sys',md5("iceserv1024").hexdigest(),md5("iceserv").hexdigest(),'SYSTEM'])
            print "created database"
        else:
            print "error.not_open"

    def price_clear(self):
        self.run('delete from tb_price_shk where idreg=%d and idprice=%d' % (self.idreg,self.price['id']))
        return self.run('delete from tb_price where idreg=%d and idprice=%d' % (self.idreg,self.price['id']))

    def price_add(self,values):
        values.insert(0,self.idreg)
        values.insert(1,self.price['id'])
        self.run(self.tb_price._add(values))

    def price_upd(self,values,_type):
        code=values[0]
        r=self.get(self.tb_price._get(self.idreg,code))
        if len(r)>0:
            struct=self.tb_price.result2values(values,decode=False)
            if _type=='clear':
                pass
            elif _type=='keep' or _type=='add':
                ost=struct['ostatok']
                del struct['ostatok']
            self.run(self.tb_price._upd(self.idreg,self.price['id'],code,struct))
            if _type=='add':
                self.run(self.tb_price._upd_grow(self.idreg,self.price['id'],code,ost))
        else:
            values.insert(0,self.idreg)
            values.insert(1,self.price['id'])
            self.price_add(values)

    def price_add_shk(self,values):
        values.insert(0,self.idreg)
        values.insert(1,self.price['id'])
        if not self.run(self.tb_price_shk._add(values)):
            pass
            #print values

    def price_upd_shk(self,code,shk,values):
        r=self.get(self.tb_price_shk._get(self.idreg,self.price['id'],code,shk))
        if len(r)>0:
            self.run(self.tb_price_shk._upd(self.idreg,self.price['id'],code,shk,values))
        else:
            self.price_add_shk([self.idreg,self.price['id'],code,shk]+values)

    def price_load(self,fname):
        """ IceCash format like Shtrihm
            1   : Код товара
            2   : Штрихкод
            3   : Наименование
            4   : reserved1
            5   : Цена
            6   : Остаток
            7   : *Схема скидок
            8   : Признак весового товара
            9   : Номер секции
            10  : *Максимальная скидка
            11  : *Тип номенклатуры
            12  : Признак алкоголя по ЕГАИС
            13  : *Минимальная цена
            14  : *Максимальная цена
            15  : reserved2
            16  : Идентификатор группы этого товара
            17  : Признак товара (не группы)
        """
        try:
            f = open(fname,'r')
        except:
            return False
        line = f.readline()
        line=line.rstrip("\n\r")

        Shash = Str2Shash(line,";","=")
        if not Shash.has_key("#IceCash"):
            print "price_load: error: not #IceCash file"
            f.close()
            return False
        if not Shash.has_key("type"):
            print "price_load: error: no type param "
            f.close()
            return False
        if Shash["type"]!="price":
            print "price_load: error: type<>IceCash.price"
            f.close()
            return False
        if not Shash.has_key("sheme_record"):
            Shash["sheme_record"]="clear"
        if not Shash.has_key("sheme_count"):
            Shash["sheme_count"]="clear"

        if Shash["sheme_record"]=="clear":
            print "price_load: clear"
            insert=True
            self.price_clear()
        else:
            insert=False

        for line in f.readlines():
            if line=='':
                continue
            line=line.decode('cp1251').encode('utf8').rstrip("\r\n")
            arr=line.split(';')
            code=arr[0]
            pref = code[0]
            if re.match(r'^#(\d)*$',code):
                if len(arr)<6:
                    continue
                (code,shk,n1,n2,cena,koef)=arr[0:6]
                code=code.lstrip('#')
                if koef=="" or koef=="0":
                    koef=1
                if not insert:
                    self.price_upd_shk(code,shk,[n1,cena,koef])
                else:
                    self.price_add_shk([code,shk,n1,cena,koef])
            elif re.match(r'^(\d)*$',code):
                if len(arr)<17:
                    continue
                if not insert:
                    self.price_upd(arr,Shash['sheme_count'])
                else:
                    self.price_add(arr)
        return True
"""
db = dbIceCash(DATABASE, "localhost", MYSQL_USER, MYSQL_PASSWORD)
if db.open():
#    db.price_load("site/download/price/pos1.spr")
    db._check_create(112)
    db.close()
"""
