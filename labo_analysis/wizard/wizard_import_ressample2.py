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

_form_cont = '''<?xml version="1.0"?>
<form string="%s">
    <field name="file_name" string="File Name" />
     <field name="attach" string="%s" filename="file_name" />
</form>''' % ('Import Setup File', 'File to import')
_send_fields_1 = {
    'attach':{'string':'Attachment', 'type':'binary'},
    'file_name':{'string':'File Name', 'type':'char', 'size':'64'} 
}


def _convert_file(self, cr, uid, data, context):
    fields={'allele1_dog':False,
            'allele2_dog': False,
            'progenus_number':False,
            'marker_dog':False
            }
    content=base64.decodestring(data['form']['attach'])
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    obj_allele=pooler.get_pool(cr.dbname).get('dog.allele')
    obj_allele_h=pooler.get_pool(cr.dbname).get('dog.allele.history')
    obj_setup=pooler.get_pool(cr.dbname).get('analysis.setup')
    obj_type=pooler.get_pool(cr.dbname).get('labo.analysis.type')
    v_hist = pooler.get_pool(cr.dbname).get('file.history')
    
    file_name=data['form']['file_name']

    list= content.split('\n')[1:]
#    name_sort=file_name[0].split('-')
#    type_s=name_sort[0].upper()
#    page_n=name_sort[1].upper()
    re= content.split('\n')[:1][0].split('\t')

#    type_id=obj_type.search(cr,uid,[('code','like',type_s)])
#    setup_page=name_sort[1]
 #   cr.execute("SELECT s.progenus_number from labo_analysis_type t, labo_analysis_request r,labo_setup ls, labo_sample s, analysis_setup e where e.set_up=ls.id and s.file_setup=e.id and ls.name='%s' and r.type_id=t.id and s.sample_id=r.id and t.code = '%s' "%(setup_page, type_s))
    flag=''
    sample_name=''
    z=0
    grp_dog_alleles={}
   # for item in list:
    try:
        for line in csv.DictReader(list, re, delimiter='\t'):
            if 'Run Name' not in line.keys():
               raise wizard.except_wizard('Error!', 'Please check the structure of your file. \n The column "Run Name" does not exist')
            l=[]
           # l=item.split('\t')
            if len(line):
                cr.execute("select id from labo_dog where progenus_number='%s' order by create_date desc "%(line['Sample Name'].strip()))
                res=cr.fetchone()
                result=res and res[0] or None
                if result:
                    ids_dogs=obj_dog.browse(cr,uid, result)
                    for v_id in ids_dogs.allele_ids:
                        obj_allele_h.create(cr,uid, {'allele_dog1':v_id.allele_dog1,
                                               'allele_dog2':v_id.allele_dog2,
                                               'marker_dog':v_id.marker_dog,
                                               'creation_date':v_id.creation_date,
                                               'dog_id1':result
                        })

                    cr.execute("delete from dog_allele where dog_id1=%d "%(result))
    except Exception, e:
        raise wizard.except_wizard('Error!',' Please check your file. \n The structure seems not to be correct: %s' %( e,))

    dict_dogs={}
    for line in csv.DictReader(list, re, delimiter='\t'):
        try:
            z+=1
            cr.execute("select id from labo_dog where progenus_number='%s' order by create_date"%(line['Sample Name'].strip()))
            res=cr.fetchone()
            result=res and res[0] or None
            if len(line)>1 and result :
                if result:
                    ids_dogs=obj_dog.browse(cr,uid, result)
                    dict_dogs[line['Sample Name']]=ids_dogs.id
                    for id_dog in ids_dogs.allele_ids:
                        grp_dog_alleles[id_dog]=result
                  #  try:
	          	obj_dog.write(cr,uid, [result], {'state': 'ok'})
                    if ids_dogs.file_setup and 'Run Name' in line:
                       obj_setup.write(cr,uid,[ids_dogs.file_setup.id], {'run_setup': line['Run Name'] or ''})
               #     except:
               #         raise wizard.except_wizard('Error!', 'Please check the structure of your file. \n The column "Run Name" does not exist')
 
                    # ===> EMPDOG
                    obj_allele.create(cr,uid, {'allele_dog1':line['Allele 1'].strip(),
                                               'allele_dog2':line['Allele 2'].strip(),
                                               'marker_dog':line['Marker'].strip(),
                                               'dog_id1':result
                                               })
                else:
                    cr.execute("select id from labo_sample where progenus_number = '%s'"%(line['Sample Name'].strip()))
#                    cr.execute("SELECT l.id from analysis_setup sa, labo_sample l, labo_setup s where l.progenus_number='%s' and s.name='%s' and sa.set_up=s.id and s.id=l.file_setup"%(l[0].strip(),page_n ))
                  #  info_ids = pooler.get_pool(cr.dbname).get('labo.sample').search(cr, uid,[('progenus_number','=',l[0].strip())])
                    res1=cr.fetchone()
                    res_id=res1 and res1[0]
                    if res_id:
                        v_infos=obj_sample.browse(cr,uid,res_id)
                        if sample_name != l[0] :
                            flag=0
                        if flag==0 :
                           # ids=obj_sample.search(cr, uid,[('progenus_number','=',l[0])])
                            if int(line['Allele 2'].strip())>0 and int(line['Allele 1'].strip()>0) :
                                state='ok' 
                            else:
                                state='zero'
                            obj_sample.write(cr, uid, res_id , {'marker':line['Marker'].strip(),
                                                                'allele1': line['Allele 2'].strip(),
                                                                'allele2':line['Allele 2'].strip(), 
                                                                'state': state })
                            sample_name=line['Sample Name'].strip()
                            flag=1
                        else:
                            try:
                                if int(line['Allele 2'].strip())>0 and int(line['Allele 1'].strip()>0) :
                                    state='ok' 
                                else:
                                    tate='zero'
                                print "line['Alelle 1']",int(line['Allele 1'].strip())
                                obj_sample.create(cr, uid, {'allele1': int(line['Allele 1'].strip()),
                                                        'allele2':int(line['Allele 2'].strip()),
                                                        'progenus_number':v_infos.progenus_number,
                                                        'state':state,
                                                        'file_setup':v_infos.file_setup.id,
                                                        'sample_id':v_infos.sample_id.id,
                                                        'code':v_infos.code,
                                                        'sanitel':v_infos.sanitel,
                                                        'material':v_infos.material,
                                                        'marker':line['Marker']
                                                        })
                                sample_name=line['Sample Name'].strip()
                            except:
                                raise wizard.except_wizard('Please check your file', ' "%s" contains incorrect values! ' %( file_name[0],))
        except Exception, e:
            raise wizard.except_wizard('Error', ' %s \n \n Please check this line! \n \n %s ' %( e,line.values(),))
        
                                        
    for r in dict_dogs:
        v_hist.create(cr,uid,{'name': data['form']['file_name'],
                           'date_f': time.strftime('%Y-%m-%d'),
                           'dog_id1':dict_dogs[r]})


#            if type_s=='EMPDOG':
#                cr.execute("select t.code,r.id,r.name,d.progenus_number,d.id,s.id from analysis_setup asd, labo_setup st,labo_sample s, labo_analysis_request r,labo_analysis_type t, labo_dog d where s.sample_id=r.id and r.type_id=t.id and d.id=s.dog_child and d.progenus_number='%s' and s.file_setup=asd.id and st.id=asd.set_up and st.name='%s'"%(l[0],page_n))
#                res=cr.fetchone()
#                result=res and res[0]
#                if res:
#                    if flag!=l[0]:
#                        obj_sample.write(cr,uid,[res[5]],{'allele1_dog': l[2].strip(),
#                                                    'allele2_dog':l[3].strip(),
#                                                    'marker_dog':l[1].strip(),
#
#                        })
#                        flag=l[0]
#                    else:
#                        new_id=obj_sample.copy(cr, uid, res[5],{'allele1_dog': l[2].strip(),
#                                                    'allele2_dog':l[3].strip(),
#                                                    'marker_dog':l[1].strip()})
#                        flag=l[0]
#
    
    return {}

class import_file_ressample(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_form_cont , 'fields': _send_fields_1, 'state':[('end','Cancel'), ('done','Import')]}
        },
        'done': {
            'actions': [_convert_file],
            'result': {'type': 'state', 'state':'end'}
        }
    }
import_file_ressample('import.ressample')
