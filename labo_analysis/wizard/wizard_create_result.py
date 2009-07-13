
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
import StringIO
from time import strftime
import time
_send_form = '''<?xml version="1.0"?>

<form string="Create .res for client">
    <field name="data" readonly="1" colspan="4"/>
</form>'''

_send_fields = {
'data': {'string':'File', 'type':'binary', 'readonly': True,},
}

view_form_finish="""<?xml version="1.0"?>
<form string="Export Analysis Result">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Export done" colspan="4"/>
        <field name="data" readonly="1" colspan="3" filename="file_name" />
        <label align="0.0" string="Save this document to a .CSV file and open it with\n your favorite spreadsheet software." colspan="4"/>
    </group>
</form>"""
_send_fields1 = {
}
def _create_file1(self, cr, uid, data, context):
    v_req = pooler.get_pool(cr.dbname).get('labo.analysis.request').browse(cr, uid, data['ids'], context)
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    buf=StringIO.StringIO()
    keys=['Sample Name','Marker','Allele1','Allele2']
    writer=csv.writer(buf, 'TINY', delimiter='\t', lineterminator='\r\n')
    keys={'Sample Name':'Sample Name','Marker':'Marker','Allele1':'Allele1','Allele2':'Allele2'}
    name_report=""
    a=''
    t=[]
    recep_date=v_sample and v_sample[0].sample_id and v_sample[0].sample_id.date_awe 
    name_report=(v_sample and v_sample[0].sample_id and v_sample[0].sample_id.type_id.code) +'/'+(v_sample and v_sample[0].sample_id and v_sample[0].sample_id.name)
    if recep_date:
        a=time.strftime('%d/%m/%Y', time.strptime( recep_date, '%Y-%m-%d'))
    file_n=[]
    for sample in v_sample:
        for s in sample.file_h_ids:
            if len(sample.allele_ids):
                if '.env' in s.name:
                    file_n.append(s.name)
    file_name=dict([i,0] for i in file_n if i ).keys()
    f_n=" ".join([str(x) for x in file_name if x])
 #   content='VER01'+'\t' +a +' \t'+ 'PROGENUS'+ '\t'+ 'BEL/P'+'\t'+ '\t'+ name_report
    t.append('VER01')
    t.append(a)
    t.append('PROGENUS')
    t.append('BEL/P')
    t.append(f_n)
    t.append(name_report)
    writer.writerow(t)
    state2id = dict([( x.progenus_number, x.id) for x in v_sample if x.state=='faulty_substance' or x.state=='no_substance' or x.state=='incoming_res' or x.state=='exist' or x.state=='unrealized' or x.state=='exist' or x.state=='unrealized'])
    s=[]
    l=[]
    lst_faulty=[]
    for sample in v_sample:
        row=[]
      #  for s in sample.file_h_ids:
      #      file_n.append(s.name)
      #  for i in sample:#.allele_ids:
        row=[]
        if sample.progenus_number and sample.progenus_number not in state2id:
           # var = (i.allele_dog1 and i.allele_dog1.isdigit()) and (i.allele_dog2 and i.allele_dog2.isdigit()) and ((((sample.state == 'ok') and 1)) or ( (sample.state=='faulty_substance') and 3) or (((sample.state == 'no_substance') and 2)) or (((sample.state == 'no_substance') and 2))  or 0 )
            var = ((sample.state == 'ok') and 1) or ( (sample.state=='faulty_substance') and 3) or (((sample.state == 'no_substance') and 2)) or (((sample.state == 'incoming_res') and 4)) or  ((sample.state == 'exist') and 5) or ((sample.state == 'unrealized') and 6) and ((sample.state == 'ko') and 0)   or 0 
            if var==0:
                raise wizard.except_wizard('Error', 'The analysis for the following progenus number "%s" is not ok '%(sample.progenus_number or None))
            for i in sample.allele_ids :
                row=[]
                row.append(sample.progenus_number or None)
                row.append(sample.sanitel or None)
                row.append(sample.code or None)
                row.append(var or None)
                row.append(i.marker_dog or None)
                row.append(i.allele_dog1 or None)
                row.append(i.allele_dog2 or None)
                writer.writerow(row)
        elif sample.progenus_number in state2id and sample.progenus_number not in lst_faulty:
            lst_faulty.append(sample.progenus_number)
            row=[]
            row.append(sample.progenus_number or None)
            row.append(sample.sanitel or None)
            row.append(sample.code or None)
            var = ((sample.state == 'ok') and 1) or ( (sample.state=='faulty_substance') and 3) or (((sample.state == 'no_substance') and 2)) or (((sample.state == 'incoming_res') and 4)) or  ((sample.state == 'exist') and 5) or ((sample.state == 'unrealized') and 6) and ((sample.state == 'ko') and 0)   or 0 
            row.append(var)
            writer.writerow(row)
    f_n=" ".join([str(x.replace('.env','')) for x in file_name if x])
    out=base64.encodestring(buf.getvalue())
    buf.close()
    return {'data': out, 'file_name':f_n and f_n+'.res' or 'no_name.res'}

def _create_file(self, cr, uid, data, context):
    v_req = pooler.get_pool(cr.dbname).get('labo.analysis.request').browse(cr, uid, data['ids'], context)
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')

    state2id={}
    for req in v_req:
        attach_ids = pooler.get_pool(cr.dbname).get('ir.attachment').search(cr, uid,[('res_model', '=', 'labo.analysis.request'),('res_id', '=', req.id),('datas_fname', '=like',"%txt")])
        res = pooler.get_pool(cr.dbname).get('ir.attachment').read(cr, uid, attach_ids, ['datas_fname','datas'])
        re = map(lambda x: (x['datas_fname'], base64.decodestring(x['datas'])), res)
        if not re:
            raise wizard.except_wizard('Error!', 'No .txt attached')
        file= re[0][1]
        attach_id_env = pooler.get_pool(cr.dbname).get('ir.attachment').search(cr, uid,[('res_model', '=', 'labo.analysis.request'),('res_id', '=', req.id),('datas_fname', '=like',"%env")])
        env=pooler.get_pool(cr.dbname).get('ir.attachment').browse(cr, uid,attach_id_env)
        filename=env[0].name
        filename=filename.replace('.env', '.res')
        res = pooler.get_pool(cr.dbname).get('ir.attachment').read(cr, uid, attach_id_env, ['datas_fname','datas'])
        re1 = map(lambda x: (x['datas_fname'], base64.decodestring(x['datas'])), res)
        content=""
        name_report= str(req.type_id.code) +str('/')+ str(req.name)
    #    content=content + 'VER01'+'\t' +str(req.date_reception[:10]) +' \t'+ 'PROGENUS'+ '\t'+ 'BEL/P'+'\t'+ env[0].name+ '\t'+ name_report+'\n'
        content_columns=""
        flag=0
        state2id = dict([( x.progenus_number, x.id) for x in req.sample_ids if x.state=='faulty_substance' or x.state=='no_substance'])
        #    var=0
        s=[]
        for r in req.sample_ids:
           # var = ((r.allele1>0) and (r.allele2>0) and (r.state == 'ok') and 1) or ( (r.state=='faulty_substance') and 3) or 0
            var = ((r.allele1>0) and (r.allele2>0) and (r.state == 'ok') and 1) or ( (r.state=='faulty_substance') and 3) or (r.state=='no_substance' and 2) or 0
            if var==0:
                raise wizard.except_wizard('Error', 'The analysis for the following progenus number "%s" is not ok '%(r.progenus_number))
            if r.progenus_number in state2id :
            #    content_columns+= str(r.progenus_number) + '\t' + str(r.sanitel or 0) + '\t' + str(r.code or 0) +'\t'+ str(3)+'\t' + str(r.marker or 0) + '\t' + str(r.allele1 or 0) + '\t'+ str(r.allele2 or 0) + '\n'
                cr.execute("select distinct(s.progenus_number),s.sanitel,s.code from labo_sample s, labo_analysis_request r where s.sample_id=r.id and r.id= %d and s.progenus_number=%s"%(req.id,r.progenus_number))
                res=cr.fetchone()
                s.append(res)
            #    content_columns+= str(r.progenus_number) + '\t' + str(r.sanitel or 0) + '\t' + str(r.code or 0) +'\t'+ str(3) + '\n'
                flag=1
            elif r.progenus_number not in state2id :
                content_columns+=str(r.progenus_number) + '\t' + str(r.sanitel or 0) + '\t' + str(r.code or 0) +'\t'+ str(var)+'\t' + str(r.marker or 0) + '\t' + str(r.allele1 or 0) + '\t'+ str(r.allele2 or 0) + '\n'
        l=dict([(i,0) for i in s]).keys()
        for r in l:
            content_columns+= str(r and r[0] or 0) + '\t' + str(r and r[1] or 0) + '\t' + str(r and r[2] or 0) +'\t'+ str(3) + '\n'

        a=req.date_awe[:10]
        b=a[8:10]+ '/'+ a[5:7]+'/'+a[1:4]
        content='VER01'+'\t' +str(b) +' \t'+ 'PROGENUS'+ '\t'+ 'BEL/P'+'\t'+ env[0].name+ '\t'+ name_report+'\n'+ content_columns
        content= base64.encodestring(content)
        res_id=pooler.get_pool(cr.dbname).get('ir.attachment').create(cr,uid,{'name':filename,'res_model':'labo.analysis.request','res_id':req.id,'datas':content})

    return {}

fields_form_finish={
    'data': {'string':'File', 'type':'binary', 'readonly': True,},
    'file_name':{'string':'File Name', 'type':'char'}
    }

class create_file_res(wizard.interface):
    states = {
        'init':{
            'actions': [_create_file1],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
 #   states = {
 #       'init': {
 #           'actions': [],
 #           'result': {'type': 'form', 'arch': _send_form, 'fields': _send_fields1, 'state':[('end','Cancel'), ('done','Create')]}
 #       },
 #       'done': {
 #           'actions': [_create_file1],
 #           'result': {'type': 'state', 'state':'end'}
 #       }
    }
create_file_res('labo.analysis.create')
class create_res(wizard.interface):

    def _create_file_sample(self, cr, uid, data, context):
        obj_sample = pooler.get_pool(cr.dbname).get('labo.sample')
        obj_dog = pooler.get_pool(cr.dbname).get('labo.dog')
        v_sample=obj_sample.browse(cr, uid, data['ids'], context)
        seq_obj=pooler.get_pool(cr.dbname).get('ir.sequence')
        v_hist = pooler.get_pool(cr.dbname).get('file.history')
        keys=['Sample Name','Marker','Allele1','Allele2']
        view_b=v_sample[0]
        view_type=view_b.cont
        if not view_type:
            view_type=v_sample[0].sample_id.type_id.code
       # try:
        buf=StringIO.StringIO()
    
        writer=csv.writer(buf, 'TINY', delimiter='\t', lineterminator='\r\n')
        writer.writerow(keys)
        name_f=[]
        cr.execute("SELECT number_next,code from ir_sequence where name='RBC'")
        res_cr1=cr.fetchone()
        last_f1=seq_obj.get(cr,uid,res_cr1[1])
        cr.execute("SELECT number_next,code from ir_sequence where name='RCS'")
        res_cr2=cr.fetchone()
        last_f2=seq_obj.get(cr,uid,res_cr2[1])
        l_dogs=[]
        last_f=''
        if view_type=="EMPDOG" or view_type=="EMPCHE":
            for i in v_sample:
                row=[]
                last_f=last_f1
                
               # if i.file_setup and i.file_setup.set_up:
               #     name_f.append(i.file_setup.set_up.name)
                if i.dog_mother and i.dog_mother.v_done==0:
                    for item in i.dog_mother.allele_ids:
                        if i.dog_mother.id not in l_dogs:
                            row=[]
                            row.append(i.dog_mother.progenus_number or '')
                            row.append(item.marker_dog or '')
                            row.append(item.allele_dog1 or '')
                            row.append(item.allele_dog2 or '')
                            writer.writerow(row)
                        obj_dog.write(cr,uid,[i.dog_mother.id],{'v_done':True})
                    if i.dog_mother.id not in l_dogs:
                            v_hist.create(cr,uid,{'dog_id1':i.dog_mother.id, 
                                        'name':last_f,
                                        })
                    l_dogs.append(i.dog_mother.id)
                if i.dog_father and i.dog_father.v_done==0:
                    for item in i.dog_father.allele_ids:
                        if i.dog_father.id not in l_dogs:
                            row=[]
                            row.append(i.dog_father.progenus_number or '')
                            row.append(item.marker_dog or '')
                            row.append(item.allele_dog1 or '')
                            row.append(item.allele_dog2 or '')
                            writer.writerow(row)
                    obj_dog.write(cr,uid,[i.dog_father.id],{'v_done':True})
                    if i.dog_father.id not in l_dogs:
                        v_hist.create(cr,uid,{'dog_id1':i.dog_father.id, 
                                    'name':last_f,
                                    })
                    l_dogs.append(i.dog_father.id)
                if i.dog_child and i.dog_child.v_done==0:
                    for item in i.dog_child.allele_ids:
                        row=[]
                        if i.dog_child.id not in l_dogs:
                            row.append(i.dog_child.progenus_number or '')
                            row.append(item.marker_dog or '')
                            row.append(item.allele_dog1 or '')
                            row.append(item.allele_dog2 or '')
                            writer.writerow(row)
                    obj_dog.write(cr,uid,[i.dog_child.id],{'v_done':True})
                    if i.dog_child.id not in l_dogs:
                        v_hist.create(cr,uid,{'dog_id1':i.dog_child.id, 
                                            'name':last_f,
                                            })
                    l_dogs.append(i.dog_child.id)
            out=base64.encodestring(buf.getvalue())
            buf.close()
            return {'data': out, 'file_name':last_f+'.res'}
        elif view_type=="EMPDOG_2":
            for i in v_sample:
                row=[]
                last_f=last_f2
                if i.dog_mother and i.dog_mother.v_done2==0:
                    for item in i.dog_mother.allele_ids:
                        if i.dog_mother.id not in l_dogs:
                            row=[]
                            row.append(i.dog_mother.progenus_number or '')
                            row.append(item.marker_dog or '')
                            row.append(item.allele_dog1 or '')
                            row.append(item.allele_dog2 or '')
                            writer.writerow(row)
                    obj_dog.write(cr,uid,[i.dog_mother.id],{'v_done2':True})
                    if i.dog_mother.id not in l_dogs:
                        v_hist.create(cr,uid,{'dog_id1':i.dog_mother.id, 
                                         'name':last_f,
                                        })
                    l_dogs.append(i.dog_mother.id)
                if i.dog_father and i.dog_father.v_done2==0:
                    for item in i.dog_father.allele_ids:
                        if i.dog_father.id not in l_dogs:
                            row=[]
                            row.append(i.dog_father.progenus_number or '')
                            row.append(item.marker_dog or '')
                            row.append(item.allele_dog1 or '')
                            row.append(item.allele_dog2 or '')
                            writer.writerow(row)
                    obj_dog.write(cr,uid,[i.dog_father.id],{'v_done2':True})
                    if i.dog_father.id not in l_dogs:
                        v_hist.create(cr,uid,{'dog_id1':i.dog_father.id, 
                                         'name':last_f,
                                        })
                    l_dogs.append(i.dog_father.id)
            out=base64.encodestring(buf.getvalue())
            buf.close()
            return {'data': out, 'file_name':last_f+'.res'}
           # fin_name=dict([i,0] for i in name_f ).keys()
           # a=''
           # for i in fin_name:
           #     a+=i+'+'
           # last_f=a[:-1] +'.res'
       # except IOError, (errno, strerror):
        txt="This file has no data for one of these reasons:\n 1. all analysis are done and all 'DONE' are checked \n 2. This button doesn't work with this kind of analysis"
        return {'file_name':'no_data.res','data':base64.encodestring(txt)}
    fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
        'file_name':{'string':'File Name', 'type':'char'}
    }
    states = {
        'init':{
            'actions': [_create_file_sample],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
    }
create_res('labo.sample.create')
