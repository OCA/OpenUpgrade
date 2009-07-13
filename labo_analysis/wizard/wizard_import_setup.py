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
import xlrd
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
<form string="%s">
     <field name="attach" string="%s"/>
</form>''' % ('Import Setup File', 'File to import')

 #    <field name="file_name" string="File Name" invisible="False"/>
 #    <field name="attach" string="%s" filename="file_name" />
_fields_cont = {
    'attach':{'string':'Attachment', 'type':'binary'},
#    'file_name':{'string':'File Name', 'type':'char'}

}



_form_cont_plate = '''<?xml version="1.0"?>
<form title="%s">
     <field name="attach" string="%s"/>
</form>''' % ('Import Plate File', 'File to import')

_fields_cont_plate = {
    'attach':{'string':'Attachment', 'type':'binary'},
}

def _import_attach(self, cr, uid, data, context):
    list_alpha=['A01','B01','C01','D01','E01','F01','G01','H01',
                'A02','B02','C02','D02','E02','F02','G02','H02',
                'A03','B03','C03','D03','E03','F03','G03','H03',
                'A04','B04','C04','D04','E04','F04','G04','H04',
                'A05','B05','C05','D05','E05','F05','G05','H05',
                'A06','B06','C06','D06','E06','F06','G06','H06',
                'A07','B07','C07','D07','E07','F07','G07','H07',
                'A08','B08','C08','D08','E08','F08','G08','H08',
                'A09','B09','C09','D09','E09','F09','G09','H09',
                'A10','B10','C10','D10','E10','F10','G10','H10',
                'A11','B11','C11','D11','E11','F11','G11','H11',
                'A12','B12','C12','D12','E12','F12','G12','H12'
                ]
    c=pooler.get_pool(cr.dbname).get('labo.sample').get_view_context(cr,uid,context)
    content=base64.decodestring(data['form']['attach'])
    list= content.split('\n')[1:]
    xl = tools.readexcel(file_contents = content)
    shname = xl.worksheets()
    sheetnames=[]
#	fields ={'progenus_number':False,'num_alpha':False}
    if shname:
        sh=shname[0]
        a = xl.getiter(sh)
        sheet_items = []
        for row in a:
            if len([i for i in row.values() if i]):
                sheet_items.append(row)
        sheetnames.append(sheet_items)
    req_obj=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
    labo_setup_obj=pooler.get_pool(cr.dbname).get('labo.setup')
    setup_obj=pooler.get_pool(cr.dbname).get('analysis.setup')
    setup_hist_obj=pooler.get_pool(cr.dbname).get('setup.history')
    dog_obj=pooler.get_pool(cr.dbname).get('labo.dog')
    user_obj=pooler.get_pool(cr.dbname).get('res.users')
    view_b=sample_obj.browse(cr,uid,data['ids'])[0]
    view_type=view_b.cont
    if not view_type:
        view_type=view_b.sample_id.type_id.code
    flag=''
    flag1=''
    a_set_ids=[]
    user_id=''
    for lines in sheetnames:
        first_lines=lines[:5]
        last_lines=lines[11:]
        a=first_lines[0].keys()
        set_up_n=a[0]!='F1' and a[0] or ''
        page_number=first_lines[0].values()[0]
        x1=first_lines[1].values()[0]
        date_f=first_lines[2].values()[0]
        operat=first_lines[3].values()[0]
        if operat:
            user_ids=user_obj.search(cr,uid,[('login','=',operat)])
            if user_ids:
                user_id = user_ids and user_ids[0] or None
        #continue till the 5th columns
        set_up_ids=labo_setup_obj.search(cr,uid,[('name','=',page_number)])
        set_up_id = set_up_ids and set_up_ids[0]

        if not set_up_id :#and flag!=page_number:
            flag=page_number
            set_up_id=labo_setup_obj.create(cr,uid,{'name':page_number,
                                    'date_s':date_f})
      #  #search analysis setup
      #  a_set_ids=setup_obj.search(cr,uid,[('set_up','=',set_up_id)])
      #  a_set_id=a_set_ids and a_set_ids[0] or ''
      #  if not len(a_set_ids):# and flag1!=set_up_id:
      #      a_set_id=setup_obj.create(cr,uid,{'set_up':set_up_id, 'well':c.index(a.values()[1])})
        for i in last_lines:
            prog=str(i.values()[0])
            try:
                t=list_alpha.index(i.values()[1].upper())
            except:
                raise wizard.except_wizard("Error!", "Please, Check the value '%s' in your file" %i.values()[1])
            
            a_set_ids=setup_obj.search(cr,uid,[('set_up','=',set_up_id), ('well','=',list_alpha.index(i.values()[1].upper())+1 )])
            a_set_id=a_set_ids and a_set_ids[0] or ''
            if not len(a_set_ids):
                a_set_id=setup_obj.create(cr,uid,{'set_up':set_up_id,
                                                'well':list_alpha.index(i.values()[1])+1,
                                                'run_setup': None
                })
            if view_type!='EMPDOG' and view_type!='EMPDOG_2' and view_type!='EMPCHE' and prog:
                cr.execute("select id from labo_sample where progenus_number = '%s'"%(prog))
                res2=cr.fetchall()
                li=[]
                for l in res2:
                    li.append(l[0])
                for r in li:
                    c=sample_obj.browse(cr,uid,r)
                 #   if user_id:
                 #       sample_obj.write(cr,uid,c.id,{'user_id':user_id})
            #ADD HISTORY
                    if c.file_setup and c.file_setup.set_up and c.file_setup.set_up.name and (c.file_setup.set_up.name!=str(page_number)):
                        r=setup_hist_obj.create(cr,uid,{'name':time.strftime('%Y-%m-%d'),
                                                'sample_id':c.id,
                                                'old_alpha':c.num_alpha,
                                                'setup_id2':c.file_setup.set_up.id or '',
                                                'setup_id': a_set_id #or None
                        })
                    k=sample_obj.write(cr,uid,c.id,{'num_alpha':i.values()[1],
                                                    'file_setup':a_set_id,
                                                    'state': 'ko'
                                                    })
                
            elif view_type in ('EMPDOG','EMPDOG_2','EMPCHE') and prog :
                cr.execute("select d.id from labo_dog d where d.progenus_number = '%s' "%(prog))
               # cr.execute("select l.id from labo_dog d,labo_sample l,labo_plate p where d.progenus_number = '%s'  and (l.dog_child=d.id or l.dog_father=d.id or l.dog_mother=d.id)"%(prog))
                res1=cr.fetchall()
                li=[]
                for l in res1:
                    li.append(l[0])
                for r in li:
                    c=dog_obj.browse(cr,uid,r)
                 #   if user_id:
                 #       dog_obj.write(cr,uid,c.id,{'user_id':user_id})
            #ADD HISTORY
                    if c.file_setup and c.file_setup.set_up and c.file_setup.set_up.name and (c.file_setup.set_up.name!=str(page_number)):
                        z=setup_hist_obj.create(cr,uid,{'name':time.strftime('%Y-%m-%d'),
                                                'dog_id1':c.id,
                                                'setup_id2':c.file_setup.set_up.id or '',
                                                'old_alpha':c.num_alpha,
                                                'setup_id': a_set_id
                        })
                    k=dog_obj.write(cr,uid,c.id,{'num_alpha':i.values()[1],
                                                    'file_setup':a_set_id,
                                                    'state':'ko',
                                                    })
                
    return {}

def _import_attach_plate(self, cr, uid, data, context):
    content=base64.decodestring(data['form']['attach'])
    list= content.split('\n')[1:]
    xl = tools.readexcel(file_contents = content)
    shname = xl.worksheets()
    sheetnames=[]
    for sh in shname:
        a = xl.getiter(sh)
        sheet_items = []
        for row in a:
            if len([i for i in row.values() if i]):
                sheet_items.append(row)
        sheetnames.append(sheet_items)
        req_obj=pooler.get_pool(cr.dbname).get('labo.analysis.request')
        sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
        dog_obj=pooler.get_pool(cr.dbname).get('labo.dog')
        user_obj=pooler.get_pool(cr.dbname).get('res.users')
        labo_plate_obj=pooler.get_pool(cr.dbname).get('labo.plate')
        plate_hist_obj=pooler.get_pool(cr.dbname).get('plate.history')
        setup_obj=pooler.get_pool(cr.dbname).get('analysis.setup')
        view_b=sample_obj.browse(cr,uid,data['ids'])[0]
        view_type=view_b.cont
        if not view_type:
            view_type=view_b.sample_id.type_id.code
        flag=''
        flag1=''
        a_set_ids=[]
        user_id=''
    for lines in sheetnames:
        first_lines=lines[:5]
        last_lines=lines[9:]
        a=first_lines[0].keys()
        set_up_n=a[0]!='F1' and a[0] or ''
        page_number=str(first_lines[0].values()[0]).zfill(4)
        x1=first_lines[1].values()[0]
        date_f=first_lines[2].keys()[0]
        operat=first_lines[1].values()[0]
        if operat:
            user_ids=user_obj.search(cr,uid,[('login','=',operat)])
            if user_ids:
                user_id = user_ids and user_ids[0] or None

        #continue till the 5th columns
        plate_ids=labo_plate_obj.search(cr,uid,[('name','=',page_number)])
        plate_id = plate_ids and plate_ids[0]
        if not plate_id :
            plate_id=labo_plate_obj.create(cr,uid,{'name':page_number,
                                                    'date_p':date_f or None})
        for i in last_lines:
            prog=unicode(i.values()[0]).encode('utf8')#.decode('latin1')
            if view_type!='EMPDOG' and  view_type!='EMPDOG_2' and view_type!='EMPCHE':
                cr.execute("select id from labo_sample where progenus_number = '%s'"%(prog))
                res=cr.fetchall()
                #ADD HISTORY
                li=[]
                for il in res:
                    if il[0]:
                        li.append(il[0])
                for r in li:
                    curr_sample=sample_obj.browse(cr,uid,r)
                    if curr_sample  and curr_sample.plate_id and (curr_sample.plate_id.name!=page_number):
                        jj=plate_hist_obj.create(cr,uid,{'name':time.strftime('%Y-%m-%d'),
                                                'sample_id':r,
                                                'plate_id2':curr_sample.plate_id.id,
                                                'plate_id': plate_id
                            })
                    k=sample_obj.write(cr,uid,r,{'num_alpha2':i.values()[1],
                                                'plate_id':plate_id,
                                                    })
                    sample_obj.write(cr,uid,r,{'user_id':user_id or None, 'state': 'ko'})
    
            else:
                #cr.execute("select l.id from labo_dog d,labo_sample l,labo_plate p where d.progenus_number = '%s' and  l.plate_id=p.id and p.name='%s'"%(prog,page_number))
               # cr.execute("select l.id from labo_dog d,labo_sample l,labo_plate p where d.progenus_number = '%s' and (l.dog_child=d.id or l.dog_father=d.id or l.dog_mother=d.id)"%(prog))
                cr.execute("select d.id from labo_dog d where d.progenus_number = '%s' "%(prog))
                res=cr.fetchall()
                li=[]
                for il in res:
                    if il[0]:
                        li.append(il[0])
                for r in li:
                    curr_dog=dog_obj.browse(cr,uid,r)
                    if curr_dog  and curr_dog.plate_id and (curr_dog.plate_id.name!=page_number):
                        jj=plate_hist_obj.create(cr,uid,{'name':time.strftime('%Y-%m-%d'),
                                                'dog_id1':r,
                                                'old_alpha':curr_dog.num_alpha2,
                                                'plate_id2':curr_dog.plate_id.id,
                                                'plate_id': plate_id
                            })
                    k=dog_obj.write(cr,uid,r,{'num_alpha2':i.values()[1],
                                                'plate_id':plate_id,
                                                    })
                    sample_obj.write(cr,uid,r,{'user_id':user_id or None, 'state': 'ko'})
                
    return {}
class import_setup_file(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result' : {'type' : 'form', 'arch' : _form_cont, 'fields' : _fields_cont, 'state' : [('end', 'Cancel'),('done_xsl', 'Import Setup')]}
        },
        'done_xsl': {
            'actions': [_import_attach],
            'result': {'type': 'state', 'state':'end'}
        },
    }
import_setup_file('set.up.sheet')



class import_plate_file(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result' : {'type' : 'form', 'arch' : _form_cont_plate, 'fields' : _fields_cont_plate, 'state' : [('end', 'Cancel'),('done', 'Import Sheet Plate')]}
        },
        'done': {
            'actions': [_import_attach_plate],
            'result': {'type': 'state', 'state':'end'}
        },
    }
import_plate_file('plate.sheet')
