# -*- encoding: utf-8 -*-
#
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

_form_cont = '''<?xml version="1.0"?>
<form string="%s">
    <field name="file_name" string="File Name" />
     <field name="attach" string="%s" filename="file_name" />
        <label align="0.2" string="Please check the next progenus number if your file has this column filled" colspan="4"/>
</form>''' % ('Import File', 'File to import')
_fields_cont = {
    'attach':{'string':'Attachment', 'type':'binary'},
    'file_name':{'string':'File Name', 'type':'char', 'size':'64'} 
}


def _makeDate(str1):
    date1=[]
    date1=str1.split('/')
    year=date1[2]
    month=date1[1]
    day=date1[0]
    final_date = date(string.atoi(year),string.atoi(month),string.atoi(day))
    return final_date
def _convert_file1(self, cr, uid, data, context):
    content=base64.decodestring(data['form']['attach'])
    list=[]
    list= content.split('\n')[1:]
    re= content.split('\n')[:1]
    nbr = 0
    fields ={'sanitel':False,
            'code': False,
            'name_animal': False,
            'sex': False,
            'progenus_number':False,
            'tube':False,
            'birthdate': False,
            'field_awe':False,
            'material':False,
            'awe2':False,
            'sample_id':False,
            }
    v_req = pooler.get_pool(cr.dbname).get('labo.analysis.request').browse(cr, uid, data['ids'], context)
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    obj_file=pooler.get_pool(cr.dbname).get('file.history')
    for req in v_req:
     #   attach_ids = pooler.get_pool(cr.dbname).get('ir.attachment').search(cr, uid,[('res_model', '=', 'labo.analysis.request'),('res_id', '=', req.id),('datas_fname', '=like',"%env")])
     #   res = pooler.get_pool(cr.dbname).get('ir.attachment').read(cr, uid, attach_ids, ['datas_fname','datas'])
     #   re = map(lambda x: (x['datas_fname'], base64.decodestring(x['datas'])), res)
        if not data['form']['attach']:
            raise wizard.except_wizard('Error!', 'No file attached for import')
        file_name=data['form']['file_name']#.split(' ')
   #     list=[]
        client_info=[]
       # client_info=re[0][1].split('\n')[0].split('\t')
        client_infos=re and re[0] and re[0].split('\t')
        client_info=client_infos and client_infos[3] 
        date_client=client_infos and client_infos[1] and client_infos[1].replace('/','-') or None
  #      list= re[0][1].split('\n')[1:]
        if client_infos and client_infos[3]:
            print client_infos, client_infos[3]
            partner_id=pooler.get_pool(cr.dbname).get('res.partner').search(cr, uid, [('name', '=', client_infos[3] )])
        if partner_id:
            part_l=pooler.get_pool(cr.dbname).get('res.partner').browse(cr,uid,partner_id)[0]
            v_part=part_l.property_product_pricelist.id or False
        if not partner_id:
            raise wizard.except_wizard('Error!', 'The name of the client "%s" does not exist'% (client_infos[3]))
        pooler.get_pool(cr.dbname).get('labo.analysis.request').write(cr,uid,req['id'],{#'begining_date':_makeDate(client_infos[1]) or None,
                                        'date_awe':_makeDate(client_infos[1]) or None,
                                        'ref_client': partner_id and partner_id[0] or None,
                                        'pricelist_id':v_part 
                                        })
        for item in list:
        #    seq=pooler.get_pool(cr.dbname).get('ir.sequence').get(cr, uid, 'labo.sample')
            l=[]
            l=item.split('\t')
            if not len(l) > 1:
                continue
            fields['sanitel']=l[0].decode('utf-8','replace').decode('latin-1').encode('utf-8')
            fields['code']=l[1].decode('utf-8','replace').encode('utf-8')
            fields['name_animal']=l[2].decode('utf-8','replace').encode('utf-8')
            if l[3]:
                fields['progenus_number']=l[3].decode('utf-8','replace').encode('utf-8')
            fields['sex']=l[4].decode('utf-8','replace').encode('utf-8')
            fields['birthdate']=_makeDate(l[5])
            fields['field_awe']=l[6].decode('utf-8','replace').encode('utf-8').strip()
            if l[7].decode('latin-1').encode('utf-8').strip() == 'Goutte sang congelé':
                fields['material']=l[10].decode('latin-1').encode('utf-8').strip()
            else:
                fields['material']=l[7].decode('latin-1').encode('utf-8').strip()
            fields['awe2']=l[8].decode('utf-8','replace').encode('utf-8').strip()
            fields['sample_id']=req['id']
      #      fields['progenus_number']=seq
            t=obj_sample.create(cr,uid,fields)
            file_n=obj_file.create(cr,uid,{'name': len(file_name) and file_name or 'No_Name', 'sample_id':t})
    return {}

class import_file1(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _form_cont, 'fields': _fields_cont, 'state':[('end','Cancel'), ('done','Import')]}
        },
        'done': {
            'actions': [_convert_file1],
            'result': {'type': 'state', 'state':'end'}
        }
    }
import_file1('labo.analysis.env')

def _import_infos(self, cr, uid, data, context):
    dog_obj=pooler.get_pool(cr.dbname).get('labo.dog')
    content=base64.decodestring(data['form']['attach'])
    xl = tools.readexcel(file_contents = content)
    shname = xl.worksheets()
    c=[]
    sheetnames=[]
    for sh in shname:
        a = xl.getiter(sh)
        sheet_items = []
        for row in a:
            if len([i for i in row.values() if i]):
                sheet_items.append(row)
        sheetnames.append(sheet_items)
    for lines in sheetnames:
        for line in lines:
            if line['LPCNPR']:
                dog_id=dog_obj.search(cr,uid,[('progenus_number','=',line['LPCNPR'])])
                if len(dog_id):
                    c.append(dog_id[0])
                    dog_obj.write(cr,uid,dog_id[0],{'name':line['LPCNOM'] and line['LPCNOM'].strip() or None,
                                                    'origin':line['LPCNOR'] and line['LPCNOR'].strip() or None
                    })

    return {
        'domain': "[('id','in', ["+','.join(map(str,c))+"])]",
        'name': 'My modified dogs',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'labo.dog',
        'view_id': False,
        'type': 'ir.actions.act_window'
    }

    return {}

class import_info_dogs(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _form_cont, 'fields': _fields_cont, 'state':[('end','Cancel'), ('done','Import')]}
        },
        'done': {
            'actions': [],
            'result': {'type': 'action','action': _import_infos , 'state':'end'}
        }
    }
import_info_dogs('dogs.infos')
