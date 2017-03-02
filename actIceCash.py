#!/usr/bin/python
# -*- coding: utf-8

import datetime

"""
    Actions for IceServ
    License GPL
    writed by Romanenko Ruslan
    redeyser@gmail.com
"""
IF_PLACE_IN     = "IF_PLACE_IN"
class Actions:

    def __init__(self,idreg,db):
        self.db     = db
        self.idreg  = idreg

    def _read(self):
        tlists  = self.db._tlist_gets(self.idreg)
        #print tlists
        self.tlists = {}
        for t in tlists:
            self.db._tlist_get(self.idreg,t[0])
            ct=[]
            for c in self.db.tlist_ct:
                ct.append(c[0])
            self.tlists[t[3]]=ct
        #print self.tlists
        gplaces = self.db._gplace_gets(self.idreg)
        self.gplaces= {}
        for p in gplaces:
            self.db._gplace_get(self.idreg,p[0])
            ct=[]
            for c in self.db.gplace_ct:
                ct.append(c[2])
            self.gplaces[p[2]]=ct

        actions = self.db._actions_gets(self.idreg)
        self.actions=[]
        td=datetime.date.today()
        for a in actions:
            act = self.db.tb_actions_hd.result2values(a)
            dt1=act['dt1']
            dt2=act['dt2']
            if act['isactive']==1 and dt1 <= td and dt2 >=td:
                self.actions.append(act)

    def _prepare_line(self,p):
        self.parse_line={'cmd':'','list':[],'list_pref':'','list_type':''}
        if p=="" or p[0]=="#":
            return False
        arr=p.split(" ")
        self.parse_line['cmd']=arr[0]
        isnot=False
        isgroups=False
        for a in arr:
            if a=='NOT':
                isnot=True
            if a=='GROUPS':
                isgroups=True
            if a[0]=='[' or a[0]=='(':
                if a[-1]!=']' and a[-1]!=')':
                    return False
                self.parse_line['list']=a[1:-1].split(",")
                if isgroups:
                    self.parse_line['list_type']='groups'
                if isnot:
                    self.parse_line['list_pref']='not'
                isnot=False
                isgroups=False

        #print "PARSE_line:", self.parse_line
        return True
                
    def _prepare(self,p):
        arr=p.split("\r\n")
        #print "ARR",arr
        self.parse=[]
        for a in arr:
            if self._prepare_line(a):
                self.parse.append(self.parse_line)

    def _filter_place(self,idplace):
        self.f_actions=[]
        for act in self.actions:
            self._prepare(act['_if'])
            add=True
            for p in self.parse:
                #print "PARSE_LINE",p
                if p['cmd']!=IF_PLACE_IN:
                    continue
                if p['list_type']=='groups':
                    place_in_list = False
                    for g in p['list']:
                        #print g,self.gplaces[g]
                        if idplace in self.gplaces[g]:
                            place_in_list = True
                            break
                else:
                    place_in_list = str(idplace) in p['list']
                if not place_in_list and p['list_pref']=='':
                    add=False
                    break
                if place_in_list and p['list_pref']=='not':
                    add=False
                    break

            if add:
                a={'id':act['id'],'name':act['name'],'dt1':str(act['dt1']),'dt2':str(act['dt2']),'tm1':str(act['tm1']),'tm2':str(act['tm2']),'daysweek':act['daysweek'],'_if':act['_if'],'_then':act['_then']}
                self.f_actions.append(a)

        if len(self.f_actions)>0:
            return True
        else:
            return False


