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
import string
import time

_send_form = '''<?xml version="1.0"?>
<form string="Import results">
    <separator string="Import results from '.txt'" colspan="4"/>
    <newline/>
</form>'''

_fields_cont = {
    'attach':{'string':'Attachment', 'type':'binary'},
    'file_name':{'string':'File Name', 'type':'char', 'size':'64'}

}

_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="file_name" string="File Name" />
    <field name="attach" string="%s" filename="file_name" />
    <label align="0.2" string="Please check the next progenus number if your file has this column filled" colspan="4"/>
</form>''' % ('Attach', 'File .env to import')
_send_fields = {
}

def _convert_file(self, cr, uid, data, context):
    nbr = 0
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    obj_dog=pooler.get_pool(cr.dbname).get('dog.allele')
    obj_allele_h=pooler.get_pool(cr.dbname).get('dog.allele.history')
    obj_setup=pooler.get_pool(cr.dbname).get('analysis.setup')
    v_hist = pooler.get_pool(cr.dbname).get('file.history')
    content=base64.decodestring(data['form']['attach'])
    list=[]
    list= content.split('\n')[1:]
    re= content.split('\n')[:1][0].split('\t')
    state_list=[]
    if not data['form']['attach']:
        raise wizard.except_wizard('Error!', 'No file attached for import')
    file= re[0][1]
    flag=0
    state=''
    sample_name=''
    a=[]
    prognum_list={}
    list_state={}
    prog=''
    dict_state={}
    dict_samples={}
    analysis_type=''
    analysis_type= data['form']['file_name'].split('-')[0].strip()
    for line in csv.DictReader(list, re, delimiter='\t'):
   #     if 'Run Name' not in line.keys():
   #         raise wizard.except_wizard('Error!', 'Please check the structure of your file. \n The column "Run Name" does not exist')
        cr.execute("select s.id from labo_sample s, labo_analysis_request r, labo_analysis_type t where "\
                    "s.progenus_number='%s' and s.sample_id=r.id and t.id=r.type_id and t.code ilike '%s'"%(line['Sample Name'].strip(), analysis_type))
        res=cr.fetchone()
        result=res and res[0]
        if result:
            ids_samples=obj_sample.browse(cr,uid, result)
            for v_id in ids_samples.allele_ids:
                obj_allele_h.create(cr,uid, {'allele_dog1':v_id.allele_dog1,
                                       'allele_dog2':v_id.allele_dog2,
                                       'sample_id':result,
                                       'marker_dog':v_id.marker_dog,
                                       'creation_date':v_id.creation_date,
                })

            cr.execute("delete from dog_allele where sample_id=%d "%(result))
            cr.commit()
    
    for line in csv.DictReader(list, re, delimiter='\t'):
        try:
            if prog!=line['Sample Name']:
                prog=''
            cr.execute("select s.id from labo_sample s, labo_analysis_request r, labo_analysis_type t where "\
                    "s.progenus_number='%s' and s.sample_id=r.id and t.id=r.type_id and t.code ilike '%s'"%(line['Sample Name'].strip(), analysis_type))
            res=cr.fetchone()
            res = res and res[0]
            if line['Allele 1'].isdigit() and line['Allele 2'].isdigit() :
                state='ok' 
            else:
                dict_state[line['Sample Name']]='ko'
            ids=obj_sample.search(cr, uid,[('progenus_number','=',line['Sample Name'])])
            i=obj_sample.browse(cr,uid, res)
            flag=line['Sample Name']
         #   for i in sample_ids:
            if i:
                obj_dog.create(cr,uid,{
                                    'marker_dog':line['Marker'],
                                    'allele_dog1':line['Allele 1'],
                                    'allele_dog2':line['Allele 2'],
                                    'sample_id':i.id,
                                    })
                try:
                    if i.file_setup and 'Run Name' in line:
                        obj_setup.write(cr,uid,[i.file_setup.id], {'run_setup': line['Run Name'] or ''})
                except:
                    raise wizard.except_wizard('Error!', 'Please check the structure of your file. \n The column "Run Name" does not exist')

                dict_samples[line['Sample Name']]=i.id
                
                if line['Sample Name'] in dict_state:
                    obj_sample.write(cr, uid, i.id , {'state': 'ko' })
                else:
                    obj_sample.write(cr, uid, i.id , {'state': state})
        except Exception, e:
           # raise e
            raise wizard.except_wizard('Error!', '%s \n Please check the error related to this line %s'%(e,line.values()))

            
    for r in dict_samples:
        v_hist.create(cr,uid,{'name': data['form']['file_name'],
                           'date_f': time.strftime('%Y-%m-%d'),
                           'sample_id':dict_samples[r]})
    return {}

class import_file_env(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _form_cont, 'fields': _fields_cont, 'state':[('end','Cancel'), ('done','Import')]}
        },
        'done': {
            'actions': [_convert_file],
            'result': {'type': 'state', 'state':'end'}
        }
    }
import_file_env('labo.analysis.import')
