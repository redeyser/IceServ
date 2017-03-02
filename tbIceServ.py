#!/usr/bin/python
# -*- coding: utf-8
# version 2.000
"""
    Tables of IceCashServ
"""
import my
from md5 import md5


class tb_sets(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('group','s')
        self.addfield('name','s')
        self.addfield('value','s')

    def _create(self):
        q="""create table `%s` (
        `id`    int(4) unsigned NOT NULL AUTO_INCREMENT,
        `group` char(64) default 'simple',
        `name`  char(64) default 'simple',
        `value` char(255) default '',
        primary key (`id`),
        unique  key `name` (`name`) ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _get(self,name):
        return self.query_select(['value']," where name='%s'" % name)

    def _getall(self,group=''):
        if group!='':
            _if=" where `group`='%s'" % group
        else:
            _if=""
        return self.query_all_select()+_if

    def _add(self,arrvalues):
        struct = self.set_values(['group','name','value'],arrvalues)
        return self.query_insert(struct)

    def _upd(self,name,value):
        struct = self.set_values(['value'],[value])
        return self.query_update(struct)+" where name='%s'" % name

    def _upd_post(self,post,group=''):
        struct={}
        for k in post.keys():
            struct[k]=post[k].value
        if group!='':
            _if=" and `group`='%s'" % group
        else:
            _if=""
        queries=[]
        for k,v in struct.items():
            queries.append(self.query_update({'value':v})+" where name='%s' %s" % (k,_if))
        return queries

class tb_regs(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('regid','s')
        self.addfield('adm_pass','s')
        self.addfield('client_pass','s')
        self.addfield('name','s')
        self.addfield('css','s')
        self.addfield('action','d')
        self.addfield('sets','d')
        self.record_add = self.fieldsorder[1:5] 

    def _create(self):
        q="""create table `%s` (
        `id`           int(4) unsigned NOT NULL AUTO_INCREMENT,
        `regid`        char(32) default '',
        `adm_pass`     char(32) default '',
        `client_pass`  char(32) default '',
        `name`         char(24) default '',
        `css`          char(100) default '',
        `action`       int(4) default 0,
        `sets`         int(4) default 0,
        primary key (`id`),
        key `reg` (`regid`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _add(self,arrvalues):
        struct = self.set_values(self.record_add,arrvalues)
        return self.query_insert(struct)

    def _get(self,regid="",id=0):
        if regid=="":
            _if="id=%d" % id
        else:
            _if="regid='%s'" % regid
        return self.query_all_select()+" where %s" % _if

    def _del(self,id):
        return self.query_delete("id=%d" % id)

    def _gets(self):
        return self.query_all_select()

    def _pre_post(self,struct):
        if struct.has_key("adm_pass"):
            adm_pass=md5(struct["adm_pass"]).hexdigest()
        else:
            adm_pass=""
        if struct.has_key("client_pass"):
            client_pass=md5(struct["client_pass"]).hexdigest()
        else:
            client_pass=""
        my.del_empty_hash(struct,"adm_pass")
        my.del_empty_hash(struct,"client_pass")
        my.ch_hash(struct,"adm_pass",adm_pass)
        my.ch_hash(struct,"client_pass",client_pass)
        return struct

    def _upd(self,id,struct):
        return self.query_update(struct)+" where id=%d" % id

    def _inc_action(self,id):
        return "update %s set action=action+1 where id=%d" % (self.tablename,id)

    def _inc_sets(self,id):
        return "update %s set `sets`=`sets`+1 where id=%d" % (self.tablename,id)

    def _upd_post(self,id,post):
        struct = self.post2struct(post,['adm_pass','client_pass','name','css'])
        struct = self._pre_post(struct)
        return self.query_update(struct)+" where id=%d" % id

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        struct = self._pre_post(struct)
        return self.query_insert(struct)

class tb_regs_sets(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('name','s')
        self.addfield('value','s')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""create table `%s` (
        `id`           int(4) unsigned NOT NULL AUTO_INCREMENT,
        `idreg`        int(4) ,
        `name`         char(255) default '',
        `value`        char(255) default '',
        primary key (`idreg`,`id`),
        key `n`   (`idreg`,`name`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_insert(struct)

    def _get_name(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and id=%d" % (idreg,id))

    def _gets(self,idreg):
        return self.query_all_select()+" where idreg=%d" % idreg

    def _upd_name(self,idreg,name,struct):
        return self.query_update(struct)+" where idreg=%d and name='%s'" % (idreg,name)

class tb_kasses(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idplace','d')
        self.addfield('idreg','d')
        self.addfield('nkassa','d')
        self.addfield('idprice','d')
        self.addfield('name','s')
        self.addfield('nickname','s')
        self.addfield('password','s')
        self.addfield('ip','s')
        self.addfield('css','s')
        self.addfield('date','D')
        self.addfield('time','t')
        self.addfield('up_date','D')
        self.addfield('up_time','t')
        self.addfield('off','d')
        self.addfield('version','s')
        self.addfield('upgrade','s')
        self.addfield('prn_name','s')
        self.addfield('prn_type','s')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""create table `%s` (
        `id`           int(4) unsigned NOT NULL AUTO_INCREMENT,
        `idplace`      int(4), 
        `idreg`        int(4),
        `nkassa`       tinyint(1) default 1, 
        `idprice`      int(4),
        `name`         char(255) default '',
        `nickname`     char(32) default '',
        `password`     char(32) default '',
        `ip`           char(24) default '',
        `css`          char(100) default '',
        `date`         date,
        `time`         time,
        `up_date`         date,
        `up_time`         time,
        `off`          tinyint(1) default 0, 
        `version`      char(24) default '',
        `upgrade`      char(24) default '',
        `prn_name`      char(24) default '',
        `prn_type`      char(24) default '',
        primary key (`idreg`,`id`,`idplace`,`nkassa`),
        key `ip` (`ip`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _gets_html(self,idreg):
        return "select k.*,(select name from tb_prices where idreg=k.idreg and id=k.idprice limit 1) as price from %s as k where idreg=%d" % (self.tablename,idreg)

    def _gets(self,idreg):
        return self.query_all_select()+" where idreg=%d" %idreg

    def _get_places(self,idreg):
        return self.query_all_select()+" where idreg=%d group by idplace order by id" %idreg

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _find(self,idreg,idplace,nkassa):
        #print self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d" % (idreg,idplace,nkassa)
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d" % (idreg,idplace,nkassa)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and id=%d" % (idreg,id))

    def _pre_post(self,struct):
        if struct.has_key("password"):
            password=md5(struct["password"]).hexdigest()
        else:
            password=""
        my.ch_hash(struct,"password",password)
        my.del_empty_hash(struct,"password")
        return struct

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        struct = self._pre_post(struct)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        struct = self._pre_post(struct)
        return self.query_insert(struct)

class tb_trsc_hd(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('idplace','d')
        self.addfield('nkassa','d')
        self.addfield('_id','d')

        self.addfield('date','D')
        self.addfield('time','t')

        self.addfield('type','d')
        self.addfield('iduser','d')
        self.addfield('seller','d')

        self.addfield('ncheck','d')
        self.addfield('ispayed','d')
        self.addfield('pay_nal','f')
        self.addfield('pay_bnal','f')

        self.addfield('summa','f')
        self.addfield('discount_card','s')
        self.addfield('bonus_card','s')
        self.addfield('discount_proc','f')
        self.addfield('bonus_proc','f')
        self.addfield('bonus_max','f')
        self.addfield('bonus_sum','f')

        self.addfield('bonus','f')
        self.addfield('discount_sum','f')
        self.addfield('bonus_discount','f')
        self.addfield('bonus_type','d')
        self.addfield('errors','s')
        self.addfield('up','d')
        self.addfield('isfiscal','d')
        self.addfield('egais_url','s')
        self.addfield('egais_sign','s')
        
        self.record_add = self.fieldsorder[1:] 


    def _create(self):
        q="""
        CREATE TABLE `%s` (
          `id`       int(10) unsigned NOT NULL AUTO_INCREMENT,
          `idreg`    int(4),
          `idplace`  int(4),
          `nkassa`   tinyint(2) unsigned NOT NULL,
          `_id`      int(4),

          `date`     date NOT NULL,
          `time`     time NOT NULL,

          `type`     tinyint(1) NOT NULL,
          `iduser`   int(4),
          `seller`   smallint(4) unsigned NOT NULL,

          `ncheck`   int(5) unsigned DEFAULT '0',
          `ispayed`  tinyint(1) unsigned default 0,
          `pay_nal`  double(8,2) default 0,
          `pay_bnal` double(8,2) default 0,

          `summa`     double(8,2) default 0,
          `discount_card`  varchar(24) default '',
          `bonus_card` varchar(24) default '',
          `discount_proc` double(8,4) default 0,
          `bonus_proc` double(8,4) default 0,
          `bonus_max` double(8,4) default 0,
          `bonus_sum`  double(8,2) default 0,

          `bonus`     double(8,2) default 0,
          `discount_sum`  double(8,2) default 0,
          `bonus_discount`  double(8,2) default 0,
          `bonus_type`  tinyint(1) unsigned default 0,
          `errors`    varchar(4)  default '',
          `up`      tinyint(1) default 0,  
          `isfiscal`      tinyint(1) default 0,
          `egais_url`     varchar(255) default '',
          `egais_sign`    varchar(255) default '',

          PRIMARY KEY `pl` (`idreg`,`idplace`,`nkassa`,`id`),
          KEY `ch` (`idreg`,`idplace`,`nkassa`,`_id`,`date`,`time`),
          KEY `tm` (`idreg`,`idplace`,`nkassa`,`date`,`time`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        
        return q

    def _get(self,idreg,idplace,nkassa,id):
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d and id=%d" % (idreg,idplace,nkassa,id)

    def _del(self,idreg,idplace,nkassa,id):
        return self.query_delete("idreg=%d and idplace=%d and nkassa=%d and id=%d" % (idreg,idplace,nkassa,id))

    def _find(self,idreg,idplace,nkassa,dt,tm,id):
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d and date='%s' and time='%s' and _id=%d" % (idreg,idplace,nkassa,dt,tm,id)

    def _add(self,arrvalues):
        struct = self.set_values(self.record_add,arrvalues)
        #print struct
        return self.query_insert(struct)

    def _filter(self,idreg,idplace,nkassa,dt1,dt2,tm1,tm2,ncheck,tcheck,tpay,tclose,dcard,bcard,fiscal,error,discount,bonus,summa,alco,code,group):
        e='and'
        _dt1=""
        _dt2=""
        _tm1=""
        _tm2=""
        _ncheck=""
        _tcheck=""
        _tpay=""
        _tclose=""
        _dcard=""
        _bcard=""
        _fiscal=""
        _error=""
        _discount=""
        _bonus=""
        _code=""
        _summa=""
        _alco=""
        _group=""

        if dt1:
            _dt1=e+" hd.date>='%s'" % dt1
        if dt2:
            _dt2=e+" hd.date<='%s'" % dt2
        if tm1:
            _tm1=e+" hd.time>='%s'" % tm1
        if tm2:
            _tm2=e+" hd.time<='%s'" % tm2
        if ncheck != None:
            _ncheck=e+" hd.ncheck='%s'" % ncheck
        if tcheck != None:
            _tcheck=e+" hd.type='%s'" % tcheck
        if tpay != None:
            if tpay=='0':
                _tpay=e+" pay_nal<>0 and pay_bnal=0"
            else:
                _tpay=e+" pay_nal=0 and pay_bnal<>0"
        if tclose != None:
            _tclose=e+" hd.ispayed=%s" % tclose
        if dcard != None:
            _dcard=e+" hd.discount_card<>''"
        if bcard != None:
            _bcard=e+" hd.bonus_card<>''"
        if fiscal != None:
            _fiscal=e+" hd.isfiscal=0"
        if error != None:
            _error=e+" hd.errors<>''"
        if  alco!= None:
            _alco=e+" hd.egais_sign<>''"
        if discount != None:
            _discount=e+" (hd.discount_sum+hd.bonus_discount)>%s" % discount
        if bonus != None:
            _bonus=e+" hd.bonus>%s" % bonus
        if summa != None:
            _summa=e+" (hd.summa-hd.discount_sum-hd.bonus_discount)>=%s" % summa
        if code != None:
            _code=e+" ct.code=%s" % code
        if group != None:
            _group=e+" ct.p_idgroup=%s" % group

        self.query_all_select()
        #q= "select hd.* from tb_trsc_hd as hd,tb_trsc_ct as ct where hd.id=ct.idhd and idplace=%d and nkassa=%d %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s order by id"\
        q= "select distinct hd.* from tb_trsc_hd as hd,tb_trsc_ct as ct where \
        hd.idreg=%d and hd.idplace=%d and hd.nkassa=%d and ct.idplace=hd.idplace and ct.idreg=hd.idreg and ct.nkassa=hd.nkassa and hd.id=ct.idhd %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s order by id"\
        % (idreg,idplace,nkassa,_dt1,_dt2,_tm1,_tm2,_ncheck,_tcheck,_tpay,_tclose,_dcard,_bcard,_fiscal,_error,_discount,_bonus,_summa,_alco,_group,_code)
        #print q
        return q

    def _get_check(self,idreg,idplace,nkassa,id):
        q=self.query_all_select()+" where idreg=%d and id=%d and idplace=%d and nkassa=%d" % (idreg,id,idplace,nkassa)
        return q

class tb_trsc_ct(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('idplace','d')
        self.addfield('nkassa','d')
        self.addfield('idhd','d')

        self.addfield('date','D')
        self.addfield('time','t')

        self.addfield('code','d')
        self.addfield('storno','d')

        self.addfield('p_idgroup','d')
        self.addfield('p_section','d')
        self.addfield('p_cena','d')
        self.addfield('p_sheme','d')
        self.addfield('p_max_skid','f')
        self.addfield('p_real','d')
        self.addfield('p_type','d')
        self.addfield('p_alco','d')
        self.addfield('p_minprice','f')
        self.addfield('p_maxprice','f')

        self.addfield('multiprice','d')

        self.addfield('paramf1','f')
        self.addfield('paramf2','f')
        self.addfield('paramf3','f')

        self.addfield('mark','s')
        self.addfield('dcount','f')
        self.addfield('discount','f')
        self.addfield('bonus','f')
        self.addfield('bonus_discount','f')
        self.addfield('p_litrag','f')
        self.addfield('p_shk','s')
        self.addfield('barcode','s')
        self.record_add = self.fieldsorder[0:] 


    def _create(self):
        q="""
        CREATE TABLE `%s` (
          `id`          int(4),
          `idreg`       int(4),
          `idplace`  int(4),
          `nkassa`   tinyint(2) unsigned NOT NULL,
          `idhd`        int(4),
          `date`        date NOT NULL,
          `time`        time NOT NULL,
          `code`        varchar(24) default '',
          `storno`      tinyint(1) default 0,

          `p_idgroup`  varchar(24) DEFAULT '0',
          `p_section`  tinyint(1)  DEFAULT 1,
          `p_cena`     double(8,2) default 0,
          `p_sheme`    tinyint(1)  default 0,
          `p_max_skid` double(8,2) default 0,
          `p_real`     tinyint(1)  default 0,
          `p_type`     tinyint(1)  default 0,
          `p_alco`     tinyint(1)  default 0,
          `p_minprice` double(8,2) default 0,
          `p_maxprice` double(8,2) default 0,

          `multiprice` tinyint(3) unsigned default 0,

          `paramf1`  double(8,2) DEFAULT 0,
          `paramf2`  double(7,3) DEFAULT 1,
          `paramf3`  double(8,2) DEFAULT 0,
          `mark`     char(6) default '',
          `dcount`   double(7,3),

          `discount`  double(8,2) DEFAULT 0,
          `bonus`  double(8,2) DEFAULT 0,
          `bonus_discount`  double(8,2) default 0,
          `p_litrag` double(8,3) default 0,
          `p_shk`     varchar(24) DEFAULT '0',
          `barcode`   varchar(68) default '',

          PRIMARY KEY `pl` (`idreg`,`idplace`,`nkassa`,`idhd`,`id`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        
        return q

    def _get(self,idreg,idplace,nkassa,id):
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d and idhd=%d" % (idreg,idplace,nkassa,id)

    def _del(self,idreg,idplace,nkassa,id):
        return self.query_delete("idreg=%d and idplace=%d and nkassa=%d and idhd=%d" % (idreg,idplace,nkassa,id))

    def _add(self,arrvalues):
        struct = self.set_values(self.record_add,arrvalues)
        #print struct
        return self.query_insert(struct)

    def _get_title(self,idreg,idplace,nkassa,id):
        self.query_all_select()
        q="select ct.*,(select pr.name from tb_price as pr,tb_kasses as ks where ks.idplace=ct.idplace and ks.idreg=ct.idreg and pr.idprice=ks.idprice and pr.idreg=ct.idreg and ct.code=pr.id)as name \
        from %s as ct where idreg=%s and idplace=%s and nkassa=%s and `idhd`=%s" % (self.tablename,idreg,idplace,nkassa,id)
        print q
        return q

class tb_prices(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('name','s')
        self.addfield('date','D')
        self.addfield('time','t')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `id`          int(4) AUTO_INCREMENT,
      `idreg`       int(4),
      `name`        varchar(255) NOT NULL,
      `date`        date,
      `time`        time,
      PRIMARY KEY (`idreg`,`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()


    def _gets(self,idreg):
        return self.query_all_select()+" where idreg=%d" % idreg

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _find(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and id=%d" % (idreg,id))

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_insert(struct)

class tb_price(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('idreg','d')
        self.addfield('idprice','d')
        self.addfield('id','s')
        self.addfield('shk','s')
        self.addfield('name','s')
        self.addfield('litrag','f')

        self.addfield('cena','f')
        self.addfield('ostatok','f')
        self.addfield('sheme','d')
        self.addfield('real','d')

        self.addfield('section','d')
        self.addfield('max_skid','f')
        self.addfield('type','d')
        self.addfield('alco','d')

        self.addfield('minprice','f')
        self.addfield('maxprice','f')
        self.addfield('reserved2','s')
        self.addfield('idgroup','s')
        self.addfield('istov','d')

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `idreg`       int(4),
      `idprice`     int(4),
      `id`          varchar(24) NOT NULL DEFAULT '',
      `shk`         varchar(13) DEFAULT NULL,
      `name`        varchar(255) NOT NULL,
      `litrag`      double(15,3) DEFAULT 0,

      `cena`        double(15,2) unsigned NOT NULL DEFAULT '0.00',
      `ostatok`     double(17,3) unsigned NOT NULL DEFAULT '0.000',
      `sheme`       tinyint(1) NOT NULL DEFAULT '0',
      `real`        tinyint(1) NOT NULL DEFAULT '0',

      `section`     smallint(2) NOT NULL DEFAULT '0',
      `max_skid`    double(5,2) NOT NULL DEFAULT '0.0',
      `type`        tinyint(1) NOT NULL DEFAULT '0',
      `alco`        tinyint(1) NOT NULL DEFAULT '0',

      `minprice`    double(15,2) NOT NULL DEFAULT '0.00',
      `maxprice`    double(15,2) NOT NULL DEFAULT '0.00',

      `reserved2`   varchar(24) DEFAULT NULL,
      `idgroup`     varchar(24) DEFAULT NULL,
      `istov`       tinyint(1) NOT NULL DEFAULT '0',

      PRIMARY KEY (`idreg`,`idprice`,`id`),
      KEY `name` (`idreg`,`idprice`,`name`,`shk`),
      KEY `idgroup` (`idreg`,`idprice`,`idgroup`,`id`),
      KEY `section` (`idreg`,`idprice`,`section`,`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q


    def _get_group(self,idreg,idprice,parent):
        return self.query_all_select()+" where idgroup='%s' and idprice=%d and idreg=%d order by istov,name" % (parent,idprice,idreg)

    def _get(self,idreg,idprice,code):
        if code!=None:
            _if=" and id='%s'" % code
        else:
            _if=""
        return self.query_all_select()+" where idreg=%d and idprice=%d %s" % (idreg,idprice,_if)

    def _find_shk(self,idreg,idprice,shk):
        return self.query_all_select()+"where idreg=%d and idprice=%d and shk='%s'" % (idreg,idprice,shk)

    def _add(self,values):
        #print values
        struct=self.set_all_values(values)
        #print struct
        return self.query_insert(struct)

    def _upd(self,idreg,idprice,code,struct):
        return self.query_update(struct)+" where idreg=%d and idprice=%d and id='%s'" % (idreg,idprice,code)

    def _upd_grow(self,idreg,idprice,code,ost):
        return "update %s set ostatok=ostatok+%s where id='%s' and idreg=%d and idprice=%d" % (self.tablename,ost,code,idreg,idprice)

class tb_price_shk(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('idreg','d')
        self.addfield('idprice','d')
        self.addfield('id','d')
        self.addfield('shk','s')
        self.addfield('name','s')
        self.addfield('cena','f')
        self.addfield('koef','f')

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `idreg`       int(4),
      `idprice`     int(4),
      `id`          varchar(24) NOT NULL DEFAULT '',
      `shk` varchar(13) NOT NULL DEFAULT '',
      `name` varchar(255) NOT NULL,
      `cena` double(15,2) unsigned NOT NULL DEFAULT '0.00',
      `koef` double(17,3) unsigned NOT NULL DEFAULT '0.000',
      PRIMARY KEY (`idreg`,`idprice`,`id`,`shk`,`cena`),
      KEY `shk` (`shk`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename

        return q

    def _get(self,idreg,idprice,code,shk=None):
        if shk!=None:
            _if=" and shk='%s'" % shk
        else:
            _if=""
        return self.query_all_select()+"where idreg=%d and idprice=%d and id='%s' %s group by cena order by cena desc" % (idreg,idprice,code,_if)

    def _find_shk(self,idreg,idprice,shk):
        return self.query_all_select()+"where idreg=%d and idprice=%d and shk='%s'" % (idreg,idprice,shk)

    def _add(self,values):
        struct=self.set_all_values(values)
        return self.query_insert(struct)

    def _upd(self,idreg,idprice,code,shk,values):
        struct = self.set_values(['name','cena','koef'],values)
        return self.query_update(struct)+" where idreg=%d and idprice=%d and id='%s' and shk='%s'" % (idreg,idprice,code,shk)

class tb_discount(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('idreg','d')
        self.addfield('idplace','d')
        self.addfield('nkassa','d')
        self.addfield('number','s')
        self.addfield('name','s')
        self.addfield('text','s')
        self.addfield('isclose','d')
        self.addfield('type','d')
        self.addfield('procent','d')

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `idreg`       int(4),
      `idplace`     int(4),
      `nkassa`      int(4),
      `number` varchar(24) NOT NULL,
      `name` varchar(100) DEFAULT 'DISCOUNT CARD',
      `text` varchar(30) DEFAULT 'discount',
      `isclose` tinyint(1) NOT NULL DEFAULT '0',
      `type` tinyint(1) NOT NULL DEFAULT '0',
      `procent` double(5,2) NOT NULL DEFAULT '20.00',
      PRIMARY KEY (`idreg`,`idplace`,`nkassa`,`number`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename

        return q

    def _get(self,code):
        return self.query_all_select()+"where number='%s' and isclose=0" % (code)

class tb_types(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('pref','s')
        self.addfield('id','d')
        self.addfield('name','s')

        self.record_add = self.fieldsorder 

    def _create(self):
        q="""create table `%s` (
        `pref`  char(8) default '',
        `id`    int(4),
        `name`  char(64) default '',
        primary key (`pref`,`id`),
        unique  key `name` (`name`) ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q


    def _add(self,arrvalues):
        struct = self.set_values(self.record_add,arrvalues)
        return self.query_insert(struct)

    def _get(self,pref):
        return self.query_select(['pref','id','name'],"pref='%s' order by name" % pref)

class tb_Zet(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('idplace','d')
        self.addfield('nkassa','d')
        self.addfield('_id','d')

        self.addfield('begin_date','D')
        self.addfield('begin_time','t')
        self.addfield('end_date','D')
        self.addfield('end_time','t')
        self.addfield('date','D')

        self.addfield('begin_ncheck','f')
        self.addfield('end_ncheck','f')

        self.addfield('summa_ret','f')
        self.addfield('c_sale','d')
        self.addfield('c_return','d')
        self.addfield('c_error','d')
        self.addfield('c_cancel','d')

        self.addfield('summa','f')
        self.addfield('summa_ret','f')
        self.addfield('summa_nal','f')
        self.addfield('summa_bnal','f')

        self.addfield('discount','f')
        self.addfield('bonus','f')
        self.addfield('bonus_discount','f')

        self.addfield('number','d')
        self.addfield('vir','f')
        self.addfield('up','d')

        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
        CREATE TABLE `%s` (
          `id`          int(4) unsigned NOT NULL AUTO_INCREMENT,
          `idreg`       int(4) default 1,
          `idplace`     int(4) default 1,
          `nkassa`      tinyint(1) default 1,
          `_id`         int(4) default 1,

          `begin_date`  date,
          `begin_time`  time,
          `end_date`    date,
          `end_time`    time,
          `date`        date,

          `begin_ncheck` int(4),
          `end_ncheck` int(4),

          `c_sale`     int(4) default 0,
          `c_return`   int(4) default 0,
          `c_error`    int(4) default 0,
          `c_cancel`   int(4) default 0,

          `summa`      double(8,2) default 0,
          `summa_ret`  double(8,2) default 0,
          `summa_nal`  double(8,2) default 0,
          `summa_bnal` double(8,2) default 0,

          `discount`   double(8,2) default 0,
          `bonus`      double(8,2) default 0,
          `bonus_discount`  double(8,2) default 0,
          `number`     int(4) default 0,
          `vir`        double(8,2) default 0,
          `up`      tinyint(1) default 0,

          PRIMARY KEY (`idreg`,`idplace`,`nkassa`,`id`),
          KEY `dt` (`idreg`,`idplace`,`nkassa`,`date`),
          KEY `up` (`idreg`,`up`,`idplace`,`nkassa`,`date`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        
        return q

    def _last(self,idplace,nkassa):
        return self.query_all_select()+"where idplace=%d and nkassa=%d order by end_date desc,end_time desc limit 1" % (idplace,nkassa)

    def _add(self,struct):
        return self.query_insert(struct)

    def _gets(self,idreg,dt1,dt2,up):
        s=""
        if up!=None:
            s+=" and up=%d" % up
        if dt1!=None:
            s+=" and date>='%s'" % dt1
        if dt2!=None:
            s+=" and date<='%s'" % dt2
        s=" where idreg=%d %s" % (idreg,s)
        return self.query_all_select()+s

    def _get(self,idreg,idplace,nkassa,id):
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d and id=%d" % (idreg,idplace,nkassa,id)

    def _find(self,idreg,idplace,nkassa,dt,id):
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d and date='%s' and _id=%d" % (idreg,idplace,nkassa,dt,id)

    def _del(self,idreg,idplace,nkassa,id):
        return self.query_delete("idreg=%d and idplace=%d and nkassa=%d and id=%d" % (idreg,idplace,nkassa,id))

    def _upd(self,idreg,idplace,nkassa,id,struct):
        return self.query_update(struct)+" where idreg=%d and idplace=%d and nkassa=%d and id=%d" % (idreg,idplace,nkassa,id)

class tb_Zet_cont(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('idplace','d')
        self.addfield('nkassa','d')
        self.addfield('idhd','d')

        self.addfield('section','d')
        self.addfield('idgroup','d')
        self.addfield('code','s')
        self.addfield('alco','d')

        self.addfield('paramf1','f')
        self.addfield('paramf2','f')
        self.addfield('paramf3','f')

        self.addfield('discount','f')
        self.addfield('bonus','f')
        self.addfield('bonus_discount','f')

        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
        CREATE TABLE `%s` (
          `id`          int(4) unsigned NOT NULL AUTO_INCREMENT,
          `idreg`       int(4) default 1,
          `idplace`     int(4) default 1,
          `nkassa`      tinyint(1) default 1,
          `idhd`        int(4) default 1,

          `section`    tinyint(1) default 0,
          `idgroup`    int(4) default 0,
          `code`       varchar(24) default 0,
          `alco`       tinyint(1) default 0,

          `paramf1`    double(8,2) default 0,
          `paramf2`    double(8,3) default 0,
          `paramf3`    double(8,2) default 0,

          `discount`   double(8,2) default 0,
          `bonus`      double(8,2) default 0,
          `bonus_discount`  double(8,2) default 0,

          PRIMARY KEY (`idreg`,`idplace`,`nkassa`,`idhd`,`id`),
          KEY `dt` (`idreg`,`idplace`,`nkassa`,`idhd`,`code`)
        ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        
        return q

    def _add(self,struct):
        return self.query_insert(struct)

    def _get(self,idreg,idplace,nkassa,id):
        return self.query_all_select()+" where idreg=%d and idplace=%d and nkassa=%d and idhd=%d" % (idreg,idplace,nkassa,id)

    def _del(self,idreg,idplace,nkassa,id):
        return self.query_delete("idreg=%d and idplace=%d and nkassa=%d and idhd=%d" % (idreg,idplace,nkassa,id))

    def _gethtml(self,idhd):
        self.query_all_select()
        return "select ct.*,pr.name from %s as ct,tb_price as pr where idhd=%d and pr.id=ct.code" % (self.tablename,idhd)

class tb_gplace_hd(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('name','s')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `id`          int(4) AUTO_INCREMENT,
      `idreg`       int(4),
      `name`        varchar(255) NOT NULL,
      PRIMARY KEY (`idreg`,`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _gets(self,idreg):
        return self.query_all_select()+" where idreg=%d" % idreg

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _find(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and id=%d" % (idreg,id))

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_insert(struct)

class tb_gplace_ct(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('ida','d')
        self.addfield('idreg','d')
        self.addfield('idplace','d')
        self.addfield('act_date','D')
        self.addfield('act_time','t')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `ida`         int(4),
      `idreg`       int(4),
      `idplace`     int(4),
      `act_date`        date,
      `act_time`        time,
      PRIMARY KEY (`idreg`,`ida`,`idplace`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _gets(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and ida=%d" % (idreg,id)

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _find(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and ida=%d" % (idreg,id))

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add(self,idreg,ida,idplace):
        struct = {'idreg':idreg,'ida':ida,'idplace':idplace}
        return self.query_insert(struct)

class tb_tlist_hd(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('idprice','d')
        self.addfield('name','s')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `id`          int(4) AUTO_INCREMENT,
      `idreg`       int(4),
      `idprice`     int(4),
      `name`        varchar(255) NOT NULL,
      PRIMARY KEY (`idreg`,`id`),
      KEY (`idreg`,`idprice`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _gets(self,idreg):
        return self.query_all_select()+" where idreg=%d" % idreg

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _find(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and id=%d" % (idreg,id))

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_insert(struct)

class tb_tlist_ct(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('ida','d')
        self.addfield('idreg','d')
        self.addfield('idt','d')
        self.addfield('dopcode','d')
        self.addfield('count','f')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `ida`         int(4),
      `idreg`       int(4),
      `idt`         int(4),
      `dopcode`     int(4),
      `count`       double(8,3) default 0,
      PRIMARY KEY (`idreg`,`ida`,`idt`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

#    def _gets(self,idreg,id):
#        return self.query_all_select()+" where idreg=%d and ida=%d" % (idreg,id)

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _gets(self,idreg,id):
        return "select ct.idt,p.name from tb_tlist_ct as ct,tb_price as p,tb_tlist_hd as t\
        where t.idreg=%d and t.idreg=p.idreg and t.idreg=ct.idreg and ct.ida=%d\
        and t.id=ct.ida and t.idprice=p.idprice and p.id=ct.idt" % (idreg,id)

    def _find(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and ida=%d" % (idreg,id))

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add(self,idreg,ida,idt):
        struct = {'idreg':idreg,'ida':ida,'idt':idt}
        return self.query_insert(struct)

class tb_actions_hd(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('idreg','d')
        self.addfield('name','s')
        self.addfield('isactive','d')
        self.addfield('dt1','D')
        self.addfield('dt2','D')
        self.addfield('tm1','t')
        self.addfield('tm2','t')
        self.addfield('daysweek','s')
        self.addfield('_if','s')
        self.addfield('_then','s')
        self.record_add = self.fieldsorder[1:] 

    def _create(self):
        q="""
      CREATE TABLE `%s` (
      `id`          int(4) AUTO_INCREMENT,
      `idreg`       int(4),
      `name`        varchar(255) NOT NULL,
      `isactive`    tinyint(1) default 0,
      `dt1`         date,
      `dt2`         date,
      `tm1`         time,
      `tm2`         time,
      `daysweek`    varchar(8) default '0000000',
      `_if`         mediumtext default '',
      `_then`       mediumtext default '',
      PRIMARY KEY (`idreg`,`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8""" % self.tablename
        return q

    def _clear(self):
        return self.empty_all_values()

    def _gets(self,idreg):
        return self.query_all_select()+" where idreg=%d order by isactive,name" % idreg

    def _get(self,idreg,id):
        return self.query_all_select()+" where idreg=%d and id=%d" % (idreg,id)

    def _find(self,idreg,name):
        return self.query_all_select()+" where idreg=%d and name='%s'" % (idreg,name)

    def _del(self,idreg,id):
        return self.query_delete("idreg=%d and id=%d" % (idreg,id))

    def _upd(self,idreg,id,struct):
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _upd_post(self,idreg,id,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_update(struct)+" where idreg=%d and id=%d" % (idreg,id)

    def _add_post(self,post):
        struct = self.post2struct(post,self.record_add)
        return self.query_insert(struct)

