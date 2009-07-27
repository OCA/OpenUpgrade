# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: wizard_spam.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import binascii
import wizard
import pooler
import tools
import base64
import csv
import StringIO
import sys
import time
import os
import string
import errno
import psycopg
import shutil
from datetime import date

def _makeDate(sdate):
    sdate=str(sdate)
    if len(sdate) == 4:
        y,m,d = sdate[2:],sdate[1:2],sdate[0:1]
    elif len(sdate) == 5:
        y,m,d = sdate[3:],sdate[1:3],sdate[0:1]
    elif len(sdate) == 6:
        y,m,d = sdate[4:],sdate[2:4],sdate[0:2]
    else:
        return ''
#        raise Exception("Format de date non reconnu %s",sdate)
    return y,m,d


_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="attach" string="%s"/>
    <field name="empdog" invisible="True" eval="1"/>
    </form>''' % ('Attach', 'File to import')


_fields_cont = {
    'attach':{'string':'Attachment', 'type':'binary'},
    'empdog':{'string':'','type':'char'}
    }


    
def _convert_attach_xsl_dog(self,cr,uid,data,context=None):
    data['form']['empdog']=True
    return _convert_attach_xsl(self,cr,uid,data,context)

def _convert_attach_xsl(self,cr,uid,data,context=None):
    fields ={}
    content=base64.decodestring(data['form']['attach'])
    list= content.split('\n')[1:]
    labo_obj=pooler.get_pool(cr.dbname).get('labo.labo')
    req_obj=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    type_obj=pooler.get_pool(cr.dbname).get('labo.analysis.type')
    sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
    dog_obj=pooler.get_pool(cr.dbname).get('labo.dog')
    seq_obj = pooler.get_pool(cr.dbname).get('ir.sequence')
    dict_s={}
    dict_s2={}
    max_v=''
    j=0
    type_id=type_obj.search(cr,uid,[('code','ilike','EMPDOG')])
    sheetnames=[]
    xl=tools.readexcel(file_contents = content)
    shname = xl.worksheets()
    for sh in shname:
        a = xl.getiter(sh)
        sheet_items = []
        for row in a:
            if len([i for i in row.values() if i]):
                sheet_items.append(row)
        sheetnames.append(sheet_items)
    for lines in sheetnames:
        for line in lines:
            dict_s[line['LPDOSS'],line['LPSEQ']]=(line['LPNRAP'],line['LPFNPR'],line['LPMNPR'],line['LPCSEX'],line['LPCTAT'],line['LPCPUC'],line['LPCNPR'],line['LPCFIL'],line['LPDTRC'])
            v_tmp=line['LPNRAP'].split('/')
            if len(v_tmp)>2:
                v_name=v_tmp[1] +'/'+ v_tmp[2]
                dict_s2[line['LPDOSS']]=(v_name)
    infos_dict=dict_s.keys()
    flag=''
    flag_is=''
    flag1=''
    list_doss=[]
    a=[]
    flag_quit=''
    flag_r=''
    flag_ss=''
    dict_p={}
    i=0
    k=sample_obj.browse(cr,uid,data['ids'])
    cr.execute("SELECT number_next,code from ir_sequence where prefix like 'cc'")
    res_cr1=cr.fetchone()
    cr.execute("SELECT number_next,code from ir_sequence where prefix like 'che'")
    res_cr2=cr.fetchone()
    while i < len(dict_s.keys()):
        infos_dict=dict_s.keys()[i]
     #   cr.execute("select s.id,s.dog_child,s.dog_mother,s.dog_father,r.id from labo_dog d, labo_analysis_request r, labo_sample s where s.sample_id=r.id and d.id=s.dog_child and d.seq=%d and s.lp_doss=%d"%(int(infos_dict[1]), int(infos_dict[0])) )
        cr.execute("select s.id,s.dog_child,s.dog_mother,s.dog_father,r.id from labo_dog d, labo_analysis_request r, labo_sample s where  d.seq=%d and s.lp_doss=%d and s.id in %s"%(int(infos_dict[1]), int(infos_dict[0]), "("+",".join(map(str,data['ids']))+")") )
        res=cr.fetchone()
        # UPDATE SAMPLES WITH RESULTS
        # RECEPTION DATE
        if res and res[0]:
            print "res",res[0]
            sample_obj.write(cr,uid,[res[0]],{'date_reception':_makeDate(dict_s.values()[i][8]) or None,
                                        'res_filiation':(dict_s.values()[i][7]) or None
        })
#        fill fields puppy
        puppy_id=res and res[1]
        print "res1",res[1],dict_s.values()[i][3]
        if puppy_id and puppy_id!=None:
            dog_obj.write(cr,uid,[puppy_id],{'tatoo':(dict_s.values()[i][4]) or None,
                                        'ship':(dict_s.values()[i][5]) or None,
                                        'sex':(dict_s.values()[i][3]) or None,
             })
            if dict_s.values()[i][6] and str(dict_s.values()[i][6])!='0':
                prog_num= dict_s.values()[i][6]
                dog_obj.write(cr,uid,[puppy_id],{'progenus_number':prog_num})
                print "iciiii"
                

#        fill fields mother
        mother_id=res and res[2]
       # if mother_id :
       #     if dict_s.values()[i][1] and str(dict_s.values()[i][1])!='0':
       #         prog_num=dict_s.values()[i][1]
       #         prog_num=seq_obj.get(cr,uid,res_cr1[1])
       #         dog_obj.write(cr,uid,[mother_id],{'progenus_number':prog_num})

#        fill fields father

        father_id=res and res[3]
        if father_id:
            if dict_s.values()[i][2] and str(dict_s.values()[i][2])!='0':
                prog_num=dict_s.values()[i][2]
                dog_obj.write(cr,uid,[father_id],{'progenus_number':prog_num})
#        fill name of request
        req_id=res and res[4]
        i+=1
        # REQUEST NUMBER FILLED IN ATTACHMENT
        # use dict_s2
        # check if request exists
    for val in dict_s2.keys():
        rek_id=''
        flag_r=''
        cr.execute("select id from labo_sample where lp_doss=%d"%(int(val)))
        ids_s=cr.fetchall()
        ids_res=ids_s and ids_s[0]
        for it in ids_s:
            cr.execute("select r.id from labo_analysis_request r, labo_analysis_type t where t.id=r.type_id and r.name like '%s' and t.code ilike 'EMPDOG'" %(dict_s2[val]))
            res_r=cr.fetchone()
            it_id=",".join([str(x) for x in it if x])
            if not res_r and flag_r!='y':
                flag_r='y'
                rek_id=req_obj.create(cr,uid,{'name': dict_s2[val], 'type_id':type_id and type_id[0]})
            elif res_r:
                res_k=res_r and res_r[0]
                rek_id=res_k
            sample_obj.write(cr,uid,[int(it_id)],{'sample_id':rek_id})
    return{}
    

class import_attach_res(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _form_cont, 'fields': _fields_cont, 'state':[('end','Cancel'),('done_xsl','Import results(xsl)')]}
        },
        'done_xsl': {
            'actions': [_convert_attach_xsl_dog],
            'result': {'type': 'state', 'state':'end'}
        },
    }
import_attach_res('labo.analysis.res')
