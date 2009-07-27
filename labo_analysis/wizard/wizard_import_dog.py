# -*- coding: iso-8859-15 -*-
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
import types
_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="attach" string="%s"/>
        <label align="0.2" string="Please check the next progenus number if your file has this column filled" colspan="4"/>
</form>''' % ('Attach', 'File to import')


_fields_cont = {
    'attach':{'string':'Attachment', 'type':'binary'}

}

fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
    }

view_form_finish="""<?xml version="1.0"?>
<form string="Export language">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Export done" colspan="4"/>
        <field name="data" readonly="1" colspan="3"/>
        <label align="0.0" string="Save this document to a .CSV file and open it with\n your favourite spreadsheet software. The file\n encoding is UTF-8. You have to translate the latest\n column before reimporting it." colspan="4"/>
    </group>
</form>"""


def _get_year(the_year):
    the_year=int(the_year)
    this_year = time.localtime(time.time())[0]
    diff = abs(this_year - (2000 + the_year)) <  abs(this_year - (1900 + the_year))
    if diff:
        return 2000+the_year
    else:
        return 1900+the_year
def makeDate(sdate):
    sdate=str(sdate)
    sdate=sdate.replace('/','').replace('-','')
    if sdate=='0' or not len(sdate):
        return None
    elif len(sdate) == 7:
        y,m,d = sdate[0:4],sdate[4:6],sdate[6:].zfill(2)
    elif len(sdate) == 8:
        y,m,d = sdate[0:4],sdate[4:6],sdate[6:]
    else:
        raise Exception("Format de date non reconnu %s",sdate)
    return str(y) + '-'+ m +'-'+d

def _makeDate(sdate):
    sdate=str(sdate)
    #sdate=sdate.replace('/','').replace('-','')
    if sdate=='0' or not len(sdate):
        return None
    if len(sdate) == 4:
        y,m,d = _get_year(sdate[2:]),sdate[1:2],sdate[0:1].zfill(2)
    elif len(sdate) == 5:
        y,m,d = _get_year(sdate[3:]),sdate[1:3],sdate[0:1].zfill(2)
    elif len(sdate) == 6:
        y,m,d = _get_year(sdate[4:]),sdate[2:4],sdate[0:2]
    elif len(sdate) == 7:
   #     if ('-' or '/') in sdate:
   #         y,m,d = _get_year(sdate[0:2]),sdate[3:5],sdate[6:].zfill(2)
   #     else:
            y,m,d = sdate[0:1],sdate[1:3],sdate[3:]
    elif len(sdate) == 8:
   #     if ('-' or '/') in sdate:
   #         y,m,d = _get_year(sdate[0:2]),sdate[3:5],sdate[6:].zfill(2)
   #     else:
            y,m,d = _get_year(sdate[6:]),sdate[2:4],sdate[0:2].zfill(2)
    elif len(sdate) == 9:
        y,m,d = sdate[0:4],sdate[3:5],sdate[6:].zfill(2)
    elif len(sdate) == 10:
      #  y,m,d = sdate[0:4],sdate[5:7],sdate[8:10]
        y,m,d = sdate[6:10],sdate[3:5],sdate[0:2]
    else:
        raise Exception("Format de date non reconnu %s",sdate)
    return str(y) + '-'+ m +'-'+d


def read_xsl(ofile):
    import win32com.client
    excel = win32com.client.Dispatch('Excel.Application')
    excel.Visible = 1
    feuille = excel.Workbooks.Open(ofile)
    listvaleur = excel.Range("A1:M500").Value
    excel.Quit()
    return listvaleur

def _convert_attach_xsl(self, cr, uid, data, context):
    content=base64.decodestring(data['form']['attach'])
    list= content.split('\n')[1:]
    labo_obj=pooler.get_pool(cr.dbname).get('labo.labo')
    doss_obj=pooler.get_pool(cr.dbname).get('doss.dog')
    req_obj=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
    dog_obj=pooler.get_pool(cr.dbname).get('labo.dog')
    partner_obj=pooler.get_pool(cr.dbname).get('res.partner')
    contact_obj=pooler.get_pool(cr.dbname).get('res.partner.address')
    type_obj=pooler.get_pool(cr.dbname).get('labo.analysis.type')
    seq_obj=pooler.get_pool(cr.dbname).get('ir.sequence')
    type_id=type_obj.search(cr, uid,[('code', 'ilike', 'EMPDOG')])
    type_id_s=type_id and type_id[0]
    type_id2=type_obj.search(cr, uid,[('code', 'ilike', 'EMPDOG_2')])
    type_id_s2=type_id2 and type_id2[0]
    type_id3=type_obj.search(cr, uid,[('code', 'ilike', 'EMPCHE')])
    type_id_s3=type_id3 and type_id3[0]
    view_type=''
    view_b=sample_obj.browse(cr,uid,data['ids'])[0]
    view_type=view_b.sample_id.type_id.code
    flag=''
    flag2=''
    flag_f=''
    flag_m=''
    pp=''
    type_a=''
    sheetnames = []
    nbr = 0
    flag1=''
    global sampleids
    sampleids = []
    header= ["LPNRAP","LPSERV","LPDOSS","LPSEQ","LPENUM","LPENOM","LPENO2","LPEADR","LPELOC","LPRACE","LPFNOM","LPFNUM","LPFTAT","LPFPUC","LPFNOR","LPFDTN","LPFRLB","LPFLLB","LPFNLB","LPFNPR","LPMNOM","LPMNUM","LPMTAT","LPMPUC","LPMNOR","LPMDTN","LPMRLB","LPMLLB","LPMNLB","LPMNPR",'LPCNOM',"LPCSEX","LPCTAT","LPCPUC","LPCDTN","LPCNPR","LPCFIL","LPFILE","LPDTRC","LPNOMT"]
    fields ={}
    fields_prelev=['name','code']
    flag_is=''
    xl = tools.readexcel(file_contents = content)
    shname = xl.worksheets()
    num_prog=''
    global flag_v
    flag_v='n'
    for sh in shname:
        a = xl.getiter(sh)
        sheet_items = []
        for row in a:
            if len([i for i in row.values() if i]):
                sheet_items.append(row)
        sheetnames.append(sheet_items)
    i=0
    for lines in sheetnames:
        for line in lines:
            try:
                fields={}
                flag_v='n'
                if not len(line):
                    continue
                view_b=sample_obj.browse(cr,uid,data['ids'])[0]
                view_type=view_b.sample_id.type_id.code
                # Try to find prelev s information
                if line['LPNRAP']:
                    res=line['LPNRAP'].split('/')
                    if len(res)>2:
                        view_type=res[0]
                        type_id=type_obj.search(cr, uid,[('code', 'ilike', view_type)])
                        type_id_s=type_id and type_id[0]
                        if view_type.upper() not in ('EMPCHE', 'EMPDOG', 'EMPDOG_2'):
                            raise wizard.except_wizard('Error!', 'You are trying to import from a non-complex analysis.\n Try to change the request name %s\n and set its type to EMPCHE, EMPDOG or EMPDOG_2 '%line['LPNRAP'])
                if view_type.upper()=="EMPDOG":
                    type_id_s=type_id_s
                    type_a='dog'
                elif view_type.upper()=="EMPDOG_2":
                    type_id_s=type_id_s2
                    type_a='dog'
                elif view_type.upper()=="EMPCHE":
                    type_id_s=type_id_s3
                    type_a='horse'
                else:
                    type_a=None
                view_type=view_type and view_type.upper()
                   # raise wizard.except_wizard('Error!', 'You are trying to import from a non-complex analysis \n Try to set a request name to "%s" \n Or import trough the menu EMPCHE, EMPDOG or EMPDOG_2  '%line['LPFNOR'])
                if line['LPSERV']:
                    fields['lp_serv']=line['LPSERV']
                try:                
                    if line['LPNOTE']:
                        fields['notice']=line['LPNOTE']
                except:
                    raise wizard.except_wizard('Error!', 'The column LPNOTE is not your file! \n Please check the structure of your file')
                if line['LPDTRC']:# and len(['LPDTRC'])>3:# and len(line['LPDTRC'])>2:

	#	pri    nt "dte", line['LPDTRC']
                    fields['date_reception']=_makeDate(line['LPDTRC']) #or ''
                fields['lp_file']=line['LPFILE']
                try:
                    if line['LPNOMT']:
                        tatoo_id=partner_obj.search(cr, uid, [('name', 'like', line['LPNOMT'])])
                        if len(tatoo_id):
                            fields['tatooer_id']=tatoo_id[0] or None
                        else:
                            # ADD Tatooer AS A PARTNER 
                            new_tatooer=partner_obj.create(cr,uid,{'name': line['LPNOMT']})
                            fields['tatooer_id']=new_tatooer or None
                except Exception, e:
                    raise wizard.except_wizard('Error!', 'The column LPNOMT is not your file! \n Please check the structure of your file: (%s)'%(e,))
                    continue

                if line['LPENOM']:
                    prelev_id=partner_obj.search(cr, uid, [('name', '=', line['LPENOM'] + ' ' + (line['LPENO2'] or '') )])
                if len(prelev_id):
                    fields['preleveur1_id']=prelev_id[0] or None
                elif not line['LPENOM']:
                    fields['preleveur1_id']=None
                else:
                    # ADD PRELEVER AS A PARTNER AND "COORDINATES"
                    new_prelev=partner_obj.create(cr,uid,{'name': line['LPENOM'] +' '+ (line['LPENO2']),
                                                        'ref':line['LPENUM'],
    
                    })
                    city_zip=line['LPELOC'].split(' ')
                    zip=''
                    zip=city_zip[0]
                    city=len(city_zip)==2 and city_zip[1] and city_zip[1:] or ''
                    new_contact_prelev=contact_obj.create(cr,uid,{'name': line['LPENOM'] + ' '+ (line['LPENO2'] or ''),
                                                                'city':city and city[0].replace('"',''),
                                                                'street':line['LPEADR'],
                                                                'zip':zip and zip.replace('"',''),
                                                                'partner_id':new_prelev
                    })
                    fields['preleveur1_id']=new_prelev or None

                    # CREATE FEMALE DOG
                # SEARCH AND CREATE LABO INFORMATION IF NOT EXISTING
                labo_femal_id=''
                dogfemal_id=''
                if line['LPFNPR'] and str(line['LPFNPR'])!='0':
                    num_prog=line['LPFNPR']
                code_femal=line['LPFNLB']
                if str(line['LPFNLB'])=='0':
                    code_femal='1'
                labofemal_id=labo_obj.search(cr,uid,[('code','=',code_femal)])
                if len(labofemal_id):
                    labo_femal_id=labofemal_id[0]
                
                elif line['LPFNLB'] and int(line['LPFNLB'])>0:
                    new_labo_f=labo_obj.create(cr,uid,{
                                                'name':line['LPFLLB'],
                                            #    'ref':line['LPFRLB'],
                                                'code':line['LPFNLB'],
                                                })
                    labo_femal_id=new_labo_f
                # Use progenus number or origin number to find femal dog
                flag2=''
                ##CHECK CONDITION TO SET 
                if line['LPFNPR'] and str(line['LPFNPR'])!='0':
                    num_prog=line['LPFNPR']
                dogfemal_id=''
                flag2=''
                if (view_type=="EMPCHE" or view_type=="EMPDOG" or view_type=="EMPDOG_2") and flag2!='y':
                    num_prog=line['LPFNPR']
                    if line['LPFNOM'] and str(line['LPFNOM'].encode('utf-8'))!='0' and (not dogfemal_id or dogfemal_id==None) and view_type=="EMPCHE":
                        dogfemal_id=dog_obj.search(cr,uid,[('name','=',line['LPFNOM'].encode('utf-8'))])
                        dogfemal_id.sort(reverse=True)
                        dogfemal_id=dogfemal_id and dogfemal_id[0]
                        flag2='y'
                    if line['LPFNPR'] and (not dogfemal_id or dogfemal_id==None):
                        dogfemal_id=dog_obj.search(cr,uid,[('progenus_number','=',line['LPFNPR'])])
                        dogfemal_id.sort(reverse=True)
                        dogfemal_id=dogfemal_id and dogfemal_id[0]
                    if line['LPFNOR'] and (not dogfemal_id or dogfemal_id==None):
                        dogfemal_id=dog_obj.search(cr,uid,[('origin','=',line['LPFNOR'])])
                        dogfemal_id.sort(reverse=True)
                        dogfemal_id=dogfemal_id and dogfemal_id[0]
                    if dogfemal_id:
                        num_tmp=dog_obj.browse(cr,uid,dogfemal_id).progenus_number
                        if not num_tmp and line['LPFNPR'] and line['LPFNPR'] and str(line['LPFNPR'])!='0':
                            dog_obj.write(cr,uid,[dogfemal_id],{'progenus_number':line['LPFNPR']})
                        if num_tmp and line['LPFNPR'] and str(line['LPFNPR'])!='0' and num_tmp!=str(line['LPFNPR']):
                            dogfemal_id=''
                    if (not(dogfemal_id) or dogfemal_id==None) and line['LPFNOM'].encode('utf8')  and line['LPFNOM'].encode('utf-8')!='0':# or not line['LPMNPR']:
                        dogfemal_id=dog_obj.create(cr,uid,{'name':line['LPFNOM'].encode('utf-8'),
                                                'progenus_number':num_prog or None,
                                                'origin':line['LPFNOR'],
                                                'tatoo':line['LPFTAT'],
                                                'sex':'F',
                                                'ref_dog':line['LPFRLB'],
                                                'race':line['LPRACE'],
                                                'birthdate':_makeDate(line['LPFDTN']),
                                                'ship':line['LPFPUC'],
                                                'pedigree':line['LPFNUM'] or None,
                                                'type_animal':type_a,
                            })
                    if labo_femal_id:
                        if dogfemal_id and dogfemal_id!=None:
                            dog_obj.write(cr,uid,[dogfemal_id],{'labo_id':labo_femal_id})
                    if dogfemal_id and dogfemal_id!=None:
                    #    if  view_type=="EMPDOG_2":
                     #       flag_v='YES'
                        fields['dog_mother']=dogfemal_id or None
                        if str(line['LPFNLB'])=='1':
                            dog_obj.write(cr,uid, [dogfemal_id], {'done_i':True})
                        doss_obj.create(cr,uid,{'name': line['LPDOSS'],
                                                'dog_id1':dogfemal_id})
                   # else:
                    #    fields['dog_mother']= None
#don t need     this part
#                if line['LPFNOM'] and view_type!='EMPCHE' and view_type!="EMPDOG" and view_type!="EMPDOG_2":
#                    if line['LPFNPR'] and str(line['LPFNPR']!='0'):
#                        dogfemal_id=dog_obj.search(cr,uid,[('progenus_number','=',line['LPFNPR'])])
#                        dogfemal_id=dogfemal_id and dogfemal_id[0]
#                        flag2='y'
#                    if line['LPMNOR'] and (not dogfemal_id or dogfemal_id==None):
#                        dogfemal_id=dog_obj.search(cr,uid,[('origin','=',line['LPFNOR'])])
#                        dogfemal_id=dogfemal_id and dogfemal_id[0]
#                  #   #   flag2='y'
#         #           if not line['LPFNPR'] and str(line['LPFNPR'])!='0' or flag2=='y':
#         #               dogfemal_id=dog_obj.search(cr,uid,[('origin','=',line['LPFNOR'])])
#         #               dogfemal_id=dogfemal_id and dogfemal_id[0]
#                    
#                    if (not(dogfemal_id) or dogfemal_id==None) and line['LPFNOM']:# or not line['LPFNPR'] or line['LPFNPR']=='0':
#                        dogfemal_id=dog_obj.create(cr,uid,{'name':line['LPFNOM'],
#                                                'progenus_number':num_prog,
#                                                'origin':line['LPFNOR'],
#                                                'tatoo':line['LPFTAT'],
#                                                'sex':'F',
#                                                'race':line['LPRACE'],
#                                                'birthdate':_makeDate(line['LPFDTN']) or None,
#                                                'ship':line['LPFPUC'],
#                                                'pedigree':line['LPFNUM'],
#                                                'type_animal':type_a,
#                                    #            'labo_id':labo_m_id
#                        })
#                    if labo_femal_id:
#                        dog_obj.write(cr,uid,[dogfemal_id],{'labo_id':labo_femal_id})
#    
#                        
#                    fields['dog_mother']=dogfemal_id
#end unusef    ul code
    
                # CREATE MALE DOG
                # SEARCH AND CREATE LABO INFORMATION IF NOT exist
                code_mal=line['LPMNLB']
                if str(line['LPMNLB'])=='0':
                    code_mal='1'
                labomal_id=labo_obj.search(cr,uid,[('code','=',code_mal)])
                labo_mal_id=''
                dogmal_id=''
                num_prog=line['LPMNPR']
                if len(labomal_id):
                    labo_mal_id=labomal_id[0]
                elif line['LPMLLB'] and line['LPMNLB'] and int(line['LPMNLB'])>0:
                    new_labo_d=labo_obj.create(cr,uid,{
                                                'name':line['LPMLLB'],
                                           #     'ref':line['LPMRLB'],
                                                'code':line['LPMNLB'],
                                                })
                    
                # Use progenus number or origin number to find mal dog
                    labo_mal_id=new_labo_d
                flag3=''
                if line['LPMNPR'] and str(line['LPMNPR'])!='0':
                    num_prog=line['LPMNPR']
                dogmal_id=''
#                if view_type=="EMPDOG_2" and flag_v=='YES':
#                    fields['dog_father']=None
                if (view_type=="EMPCHE" or view_type=="EMPDOG" or view_type=="EMPDOG_2") and flag3!='y':
               # if view_type=="EMPCHE" and flag3!='y':
                    num_prog=line['LPMNPR']
                    if (line['LPMNOM'] and str(line['LPMNOM'].encode('utf-8'))!='0') and (not dogmal_id or dogmal_id==None) and view_type=="EMPCHE":
                        dogmal_id=dog_obj.search(cr,uid,[('name','=',line['LPMNOM'].encode('utf)8'))])
                        dogmal_id.sort(reverse=True)
                        dogmal_id=dogmal_id and dogmal_id[0]
                        flag3='y'
                    if line['LPMNPR'] and (not dogmal_id or dogmal_id==None):
                            dogmal_id=dog_obj.search(cr,uid,[('progenus_number','=',line['LPMNPR'])])
                            dogmal_id.sort(reverse=True)
                            dogmal_id=dogmal_id and dogmal_id[0]
                    if line['LPMNOR'] and (not dogmal_id or dogmal_id==None):
                            dogmal_id=dog_obj.search(cr,uid,[('origin','=',line['LPMNOR'])])
                            dogmal_id.sort(reverse=True)
                            dogmal_id=dogmal_id and dogmal_id[0]
                    if dogmal_id:
                        num_tmp=dog_obj.browse(cr,uid,dogmal_id).progenus_number
                        if not num_tmp and line['LPMNPR'] and str(line['LPMNPR'])!='0':
                            dog_obj.write(cr,uid,[dogmal_id],{'progenus_number':line['LPMNPR']})
                        if num_tmp and line['LPMNPR'] and str(line['LPMNPR'])!='0' and num_tmp!=str(line['LPMNPR']):
                            dogmal_id=''

                 #   if dogmal_id:
                    if (not(dogmal_id) or dogmal_id==None) and line['LPMNOM'].encode('utf)8') and line['LPMNOM']!='0':# or not line['LPMNPR']:
                        dogmal_id=dog_obj.create(cr,uid,{'name':line['LPMNOM'].encode('utf-8'),
                                                'progenus_number':num_prog,
                                                'origin':line['LPMNOR'],
                                                'tatoo':line['LPMTAT'],
                                                'sex':'M',
                                                'race':line['LPRACE'],
                                                'ref_dog':line['LPMRLB'],
                                                'birthdate':_makeDate(line['LPMDTN']),
                                                'ship':line['LPMPUC'],
                                                'pedigree':line['LPMNUM'] or None,
                                                'type_animal':type_a,
                            })
                    if labo_mal_id and labo_mal_id!=None and dogmal_id:
                        dog_obj.write(cr,uid,[dogmal_id],{'labo_id':labo_mal_id or None})
                    if dogmal_id and dogmal_id!=None and len(str(dogmal_id)):
                   #     if flag_v!='YES':# and view_type=="EMPDOG_2":
                        fields['dog_father']=dogmal_id or None
                        if str(line['LPMNLB'])=='1':
                            dog_obj.write(cr,uid, [dogmal_id], {'done_i':True})
                        doss_obj.create(cr,uid,{'name': line['LPDOSS'],
                                                'dog_id1':dogmal_id
                        
                        } )
                       # else:
                        #    fields['dog_father']=None
#                if line['LPMNOM'] and view_type!='EMPCHE':
#                    if line['LPMNPR'] and str(line['LPMNPR'])!='0':
#                        dogmal_id=dog_obj.search(cr,uid,[('progenus_number','=',line['LPMNPR'])])
#                        dogmal_id=dogmal_id and dogmal_id[0]
#                        flag3='y'
#                    if not line['LPMNPR'] or flag3=='y':
#                            dogmal_id=dog_obj.search(cr,uid,[('origin','=',line['LPMNOR'])])
#                            dogmal_id=dogmal_id and dogmal_id[0]
#                    if not(dogmal_id) and line['LPMNOM']:# or not line['LPMNPR']:
#                        dogmal_id=dog_obj.create(cr,uid,{'name':line['LPMNOM'],
#                                                'progenus_number':num_prog,
#                                                'origin':line['LPMNOR'],
#                                                'tatoo':line['LPMTAT'],
#                                                'sex':'M',
#                                                'race':line['LPRACE'],
#                                                'birthdate':_makeDate(line['LPMDTN']),
#                                                'ship':line['LPMPUC'],
#                                                'pedigree':line['LPMNUM'] or None,
#                                                'type_animal':type_a,
#                            })
#                    if labo_mal_id:
#                        dog_obj.write(cr,uid,[dogmal_id],{'labo_id':labo_mal_id})
#                    fields['dog_father']=dogmal_id
                if line['LPDOSS']:
                    fields['lp_doss']=line['LPDOSS']
                    
                if line['LPCFIL']:
                    fields['res_filiation']=line['LPCFIL']
    
                # CREATE PUPPY
                # SEARCH AND CREATE PROGENUS LABO INFORMATION
                labop_id=labo_obj.search(cr,uid,[('code','=',1)])
                if len(labop_id):
                    labo_p_id=labop_id[0]
                else:
                    new_labo_p=labo_obj.create(cr,uid,{
                                                'name':'Progenus',
                                                'ref':'1',
                                                'code':'1',
                                                })
                    labo_p_id=new_labo_p
                # SEARCH PUPPY
                puppy_id=''
                if view_type=="EMPCHE":
                    try:
                        name=line['LPCNOM'].encode('utf-8')
                    except:
                        raise wizard.except_wizard('Error!', 'The column LPCNOM is not your file! \n Please check the structure of your file')
                    if line['LPCNOM'] and str(line['LPCNOM'].encode('utf-8'))!='0' and (not puppy_id or puppy_id==None):
                        puppy_id=dog_obj.search(cr,uid,[('name','=',line['LPCNOM'].encode('utf-8'))])
                        puppy_id=puppy_id and puppy_id[0]
                        flag2='y'
                    if  line['LPCNPR'] and str(line['LPCNPR'])!='0':
                        puppy_id=dog_obj.search(cr, uid, [('progenus_number','=', line['LPCNPR'])])
                        puppy_id=puppy_id and puppy_id[0]
                    # compare using sequence and DOSS
                        if not puppy_id or puppy_id==None:
                            m_id=dog_obj.search(cr,uid,[('name','=',line['LPMNOM'].encode('utf-8'))])
                            f_id=dog_obj.search(cr,uid,[('name','=',line['LPFNOM'].encode('utf-8'))])
                            a=m_id and m_id[0]
                            b=f_id and f_id[0]
                            if not len(f_id):
                                f_id=dog_obj.search(cr,uid,[('tatoo','=',line['LPFTAT'])])
                            else:
                                f_id=dog_obj.search(cr,uid,[('origin','=',line['LPFNOR'])])
                            b=f_id and f_id[0]
                            if not len(m_id):
                                m_id=dog_obj.search(cr,uid,[('tatoo','=',line['LPMTAT'])])
                            else:
                                m_id=dog_obj.search(cr,uid,[('origin','=',line['LPMNOR'])])
                            a=m_id and m_id[0]
                            if a  and a!=None and b and b!=None:
                                cr.execute("SELECT id from labo_dog where parent_f_id=%d and parent_m_id=%d"%(a,b))
                                res=cr.fetchone()
                                puppy_id=res and res[0]
                        else:
                            num_prog=line['LPCNPR']
                            flag1='y'
                    if not puppy_id or puppy_id==None:
                        # find mum of child
                        m_id=dog_obj.search(cr,uid,[('name','=',line['LPMNOM'].encode('utf-8'))])
                        f_id=dog_obj.search(cr,uid,[('name','=',line['LPFNOM'].encode('utf-8'))])
                        a=m_id and m_id[0]
                        b=f_id and f_id[0]
                        if a  and a!=None and b and b!=None:
                            cr.execute("SELECT id from labo_dog where parent_f_id=%d and parent_m_id=%d"%(a,b))
                            res=cr.fetchone()
                            puppy_id=res and res[0]
                        try:
                            name=line['LPCNOM'].encode('utf-8')
                        except:
                            raise wizard.except_wizard('Error!', 'The column LPCNOM is not your file! \n Please check the structure of your file')

                        if puppy_id and line['LPCNPR'] and str(line['LPCNPR'])!='0':
                            num_p=dog_obj.browse(cr,uid,puppy_id).progenus_number
                            if not num_p and line['LPCNPR']:
                                dog_obj.write(cr,uid,[puppy_id],{'progenus_number':line['LPCNPR']})
                            if num_p and line['LPCNPR'] and num_p!=str(line['LPCNPR']):
                                puppy_id=''

                        if not puppy_id or puppy_id==None:
                            puppy_id=dog_obj.create(cr,uid,{
                                                'name':line['LPCNOM'].encode('utf-8'),
                                                'progenus_number':str(line['LPCNPR'])!='0' and line['LPCNPR'],
                                             #   'seq':line['LPSEQ'],
                                                'tatoo':line['LPCTAT'],
                                                'sex':line['LPCSEX'],
                                                'race':line['LPRACE'],
                                                'birthdate':_makeDate(line['LPCDTN']),
                                                'ship':line['LPCPUC'],
                                                'parent_m_id':dogfemal_id or None,
                                                'parent_f_id':dogmal_id or None,
                                                'labo_id':labo_p_id or None,
                                                'type_animal':type_a,
                                                })
                    if puppy_id and puppy_id!=None:
                        fields['dog_child']=puppy_id
                        #dog_obj.write(cr,uid, [puppy_id], {'done_i':True})
                        doss_obj.create(cr,uid,{'name': line['LPDOSS'] or None,
                                                'dog_id1':puppy_id})
                    if line['LPSEQ']:
                        fields['seq_horse']=line['LPSEQ']
                puppy_id=''
                if view_type=="EMPDOG":
              #  ##1 
              #      if line['LPCNOM'] and str(line['LPCNOM'].encode('utf-8'))!='0' and (not puppy_id or puppy_id==None):
              #          puppy_id=dog_obj.search(cr,uid,[('name','=',line['LPCNOM'].encode('utf-8'))])
              #          puppy_id=puppy_id and puppy_id[0] or None
              #  #END of 1
                    if  line['LPCNPR'] and str(line['LPCNPR'])!='0' and (not puppy_id or puppy_id==None):
                        puppy_id=dog_obj.search(cr, uid, [('progenus_number','=', line['LPCNPR'])])
                        puppy_id=puppy_id and puppy_id[0]

                    # compare using sequence and DOSS
                        if not puppy_id:
                            m_id=dog_obj.search(cr,uid,[('origin','=',line['LPMNOR'])])
                            f_id=dog_obj.search(cr,uid,[('origin','=',line['LPFNOR'])])
                            a=m_id and m_id[0]
                            b=f_id and f_id[0]
                            c=int(line['LPSEQ'])
                            cr.execute("SELECT id from labo_dog where seq=%d and parent_f_id=%d and parent_m_id=%d"%(c,a,b))
                            res=cr.fetchone()
                            puppy_id=res and res[0]
                        else:
                            num_prog=line['LPCNPR']
                            flag1='y'
                    if not(line['LPCNPR']) or str(line['LPCNPR'])=='0' and ( not(puppy_id) or puppy_id==None):
                        # find mum of child
                        m_id=dog_obj.search(cr,uid,[('origin','=',line['LPMNOR'])])
                        f_id=dog_obj.search(cr,uid,[('origin','=',line['LPFNOR'])])
                        a=m_id and m_id[0]
                        b=f_id and f_id[0]
                        c=line['LPSEQ'] and int(line['LPSEQ'])
                        if a and a!=None and b and b!=None and c and c!=None:
                            cr.execute("SELECT id from labo_dog where seq=%d and parent_f_id=%d and parent_m_id=%d"%(c,b,a))
                            res=cr.fetchone()
                            puppy_id=res and res[0]
                    if puppy_id and line['LPCNPR'] and str(line['LPCNPR'])!='0':
                        num_p=dog_obj.browse(cr,uid,puppy_id).progenus_number
                        if not num_p and line['LPCNPR']:
                            dog_obj.write(cr,uid,[puppy_id],{'progenus_number':line['LPCNPR']})
                        if num_p and num_p!=str(line['LPCNPR']):
                            puppy_id=''
    
                    if (line['LPCNPR']) and str(line['LPCNPR'])=='0' and  puppy_id==None or not puppy_id:
                    #    num_prog=line['LPCNPR']
                   # if not puppy_id or puppy_id==None:
                        puppy_id=dog_obj.create(cr,uid,{
                                             #   'name':line['LPCNOM'],
                                                'progenus_number':line['LPCNPR'],
                                                'seq':line['LPSEQ'],
                                                'tatoo':line['LPCTAT'],
                                                'sex':line['LPCSEX'],
                                                'race':line['LPRACE'],
                                                'birthdate':_makeDate(line['LPCDTN']),
                                                'ship':line['LPCPUC'],
                                                'parent_m_id':dogfemal_id or None,
                                                'parent_f_id':dogmal_id or None,
                                                'labo_id':labo_p_id,
                                                'type_animal':type_a,
                                                })
                    if puppy_id and puppy_id!=None:
                        fields['dog_child']=puppy_id
#                        dog_obj.write(cr,uid, [puppy_id], {'done_i':True})
                        doss_obj.create(cr,uid,{'name': line['LPDOSS'] or None,
                                                'dog_id1':puppy_id})
                flag1=''
                # SET A REQUEST
                #  REQUEST FILLED IN THE ATTACHMENT
                if line['LPNRAP']:# and flag!=line['LPNRAP']:
                    res=line['LPNRAP'].split('/')
                    if len(res)>2:
                        num=res[1]+'/'+res[2]
                    # CHECK IF REQUEST ALREADY EXITS
                        if res[0]:
                            view_type=res[0]
                            type_id=type_obj.search(cr, uid,[('code', 'ilike', view_type)])
                            type_id_s=type_id and type_id[0]
                        elif view_type=="EMPDOG":
                            type_id_s=type_id_s
                        elif view_type=="EMPDOG_2":
                            type_id_s=type_id_s2
                        elif view_type=="EMPCHE":
                            type_id_s=type_id_s3
                    r_id=req_obj.search(cr,uid,[('name','=',num),('type_id','=',type_id_s)])
                    if len(r_id):
                        request_id=r_id[0]
                    else:
                        request_id=req_obj.create(cr,uid,{'type_id':type_id_s, 'name':num})
                    flag=line['LPNRAP']
                elif line['LPNRAP'] and flag==line['LPNRAP']:
                    request_id=request_id
                else:
                    has_id=req_obj.search(cr,uid,[('type_id','=',type_id_s),('name','=','0000/0000')])
                    request_id=has_id and has_id[0]
                    if not has_id and pp!='y':
                        request_id=pooler.get_pool(cr.dbname).get('labo.analysis.request').create(cr,uid,{'type_id':type_id_s, 'name':'0000/0000'})
                        pp='y'
                        flag_is='yes'
                    else:
                        request_id=request_id
                fields['sample_id']=request_id or None
                sample_id=sample_obj.create(cr,uid,fields)
                sampleids.append(sample_id)
            except Exception, e:
                raise wizard.except_wizard('Error!', '%s \n The problem is coming from this line! Please check its content \n \n %s' %(e,line.values(),))
    return {}


class import_attach(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result' : {'type' : 'form', 'arch' : _form_cont, 'fields' : _fields_cont, 'state' : [('end', 'Cancel'),('done_xsl', 'Import xls')]}
        },
        'done_xsl': {
            'actions': [_convert_attach_xsl],
            'result': {'type': 'state', 'state':'end'}
        },
    }
import_attach('labo.analysis.csv')

def _convert_simple_file(self, cr, uid, data, context):
    sheetnames = []
    content=base64.decodestring(data['form']['attach'])
    xl = tools.readexcel(file_contents = content)
    shname = xl.worksheets()
#    header= ["LPNRAP","LPSERV","LPDOSS","LPSEQ","LPENUM","LPENOM","LPENO2","LPEADR","LPELOC","LPRACE","LPFNOM","LPFNUM","LPFTAT","LPFPUC","LPFNOR","LPFDTN","LPFRLB","LPFLLB","LPFNLB","LPFNPR","LPMNOM","LPMNUM","LPMTAT","LPMPUC","LPMNOR","LPMDTN","LPMRLB","LPMLLB","LPMNLB","LPMNPR",'LPCNOM',"LPCSEX","LPCTAT","LPCPUC","LPCDTN","LPCNPR","LPCFIL","LPFILE","LPDTRC","LPNOMT"]
    fields ={}
    header=["Dossier","Numpro","date recpt","num1","num2","num3","nom","race","sexe","matiere","dtn","divers1","divers2","preleveur"]
    partner_obj=pooler.get_pool(cr.dbname).get('res.partner')
    req_obj=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
    contact_obj=pooler.get_pool(cr.dbname).get('res.partner.address')
    type_obj=pooler.get_pool(cr.dbname).get('labo.analysis.type')
    view_b=sample_obj.browse(cr,uid,data['ids'])[0]
    view_type=view_b.sample_id.type_id.code
 #   view_type=view_type.upper()
    num=''
    pp=''
    flag=''
    for sh in shname:
        a = xl.getiter(sh)
        sheet_items = []
        for row in a:
            if len([i for i in row.values() if i]):
                sheet_items.append(row)
        sheetnames.append(sheet_items)
    for lines in sheetnames:
        for line in lines:
            if line['Numpro']:
                fields['progenus_number']=line['Numpro']
            if line['date recpt']:
                fields['date_reception']=makeDate(line['date recpt']) or ''
            fields['identifier_1']=line['num1'] or None
            fields['identifier_2']=line['num2'] or None
            fields['identifier_3']=line['num3'] or None
            fields['name_animal']=line['nom'] or None
            fields['breed']=line['race'] or None
            fields['sex']=line['sexe'] or None
            fields['material']=line['matiere'] or None
            fields['birthdate']=makeDate(line['dtn']) or None
            fields['misc_1']=line['divers1'] or None
            fields['misc_2']=line['divers2'] or None
            if line['preleveur']:
                prelev_id=partner_obj.search(cr, uid, [('name', '=', line['preleveur'])])
                if len(prelev_id):
                    fields['preleveur_id']=prelev_id[0]
                else:
                    # ADD Eleveur AS A PARTNER 
                    new_tatooer=partner_obj.create(cr,uid,{'name': line['preleveur']})
                    fields['preleveur_id']=new_tatooer

            if len(line['Dossier']):# and flag!=line['Dossier']:
#	    	if '/' in line['Dossier']:
                res=line['Dossier'].split('/')
                if len(res)>2:
                    num=res[1]+'/'+res[2]
                type_name=res and res[0] or None 
		type_name=type_name.upper()
            else:
                type_name=view_type.upper()
            type_id_s=type_obj.search(cr,uid,[('code','ilike',type_name)])
            # CHECK IF REQUEST ALREADY EXITS
            if num:
                r_id=req_obj.search(cr,uid,[('name','=',num),('type_id','=', type_id_s[0])])
                if len(r_id):
                    request_id=r_id[0]
                else:
                    request_id=req_obj.create(cr,uid,{'type_id':type_id_s[0], 'name':num})
                    flag=line['Dossier']
            elif line['Dossier'] and flag==line['Dossier']:
                request_id=request_id
            else:
                has_id=req_obj.search(cr,uid,[('type_id','=',type_id_s[0]),('name','=','0000/0000')])
                request_id=has_id and has_id[0]
                if not has_id and pp!='y':
                    request_id=pooler.get_pool(cr.dbname).get('labo.analysis.request').create(cr,uid,{'type_id':type_id_s[0], 'name':'0000/0000'})
                    pp='y'
                    flag_is='yes'
                else:
                    request_id=request_id
            fields['sample_id']=request_id
            sample_id=sample_obj.create(cr,uid,fields)
    return {}
            
            


            

    return {}
class import_simple_analysis(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _form_cont, 'fields': _fields_cont, 'state':[('end','Cancel'), ('done_s','Import')]}
        },
        'done_s': {
            'actions': [_convert_simple_file],
            'result': {'type': 'state', 'state':'end'}
        }
    }
import_simple_analysis('labo.simple.analysis')
