# -*- coding: utf-8
from  dbIceCash import *
from  chIceCash import *
from  bsIceCash import *
import sys

def calc(_a):
    _a='111'
    return _a

a={1:"ahsadh",2:"2327367"}
print calc(a[1])
print a
sys.exit(1)

db = dbIceCash(DATABASE, "localhost", MYSQL_USER, MYSQL_PASSWORD)
db.open()
db._read_sets()
#db.price_load("site/download/price/pos1.spr")
iduser=1
#ch = chIceCash(db,iduser)
#ch._create()
#ch._set_type(CH_SALE)
#ch._add_tov("8")
#ch._add_tov("3204")
#ch._load(0)
#ch._calc()
#print ch._add_shk("2000000040011")
#print ch.findtype
bs=bsIceCash(1,1,"192.168.1.224",7172)
print bs.connect()
print bs.cmd_ping()
print bs.data
#print bs.cmd_info("7770000393046")
print bs.cmd_addsum("7770000085057",50,1,1)
print bs.data
print bs.cmd_closesum("7770000085057")
print bs.cmd_info("7770000085057")
#print bs.cmd_addsum("7770000085057",100,1,1)
print bs.data
print bs.info
bs.close()
db.close()
