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
import sys
_attach_form = '''<?xml version="1.0"?>
<form string="Create .txt to attach to the machine">
    <field name="owner_a" string="Owner"/>
    <field name="operator_a" string="Operator"/>
    <field name="container_a" string="Container"/>

</form>'''

#    <field name="file_name" string="File name"/>

_attach_fields = {
#    'file_name': {'string':'File name', 'type':'char', 'required':True},
    'owner_a': {'string':'Owner', 'type':'char'},
    'operator_a': {'string':'Operator', 'type':'char'},
    'container_a': {'string':'Container', 'type':'selection', 'selection': [('96-Well','96-Well'),('192-Well','192-Wells')]},

}

view_form_finish="""<?xml version="1.0"?>
<form string="Export Analysis Results">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Export done" colspan="4"/>
        <field name="data" readonly="1" colspan="3" filename="file_name" />
        <label align="0.0" string="Save this document to a .CSV file and open it with\n your favourite spreadsheet software. The file\n encoding is UTF-8." colspan="4"/>
    </group>
</form>"""
class create_file_machine(wizard.interface):
    def _create_file(self, cr, uid, data, context):
        obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
        v_sample=obj_sample.browse(cr,uid,data['ids'])
        view_b=v_sample[0]
        view_type=view_b.sample_id.type_id.code
        header_1='Container Name'+'\t'+'Description'+'\t'+'ContainerType'+'\t'+'AppType'+'\t'+'Owner'+'\t'+'Operator'+'\n'
        header_2='Well'+'\t'+'Sample Name'+'\t'+'Comment'+'\t'+'Priority'+'\t'+'Size Standard'+'\t'+'Snp Set'+'\t'+'User-Defined 3'+'\t'+'User-Defined 2'+'\t'+'User-Defined 1'+'\t'+'Panel'+'\t'+'Study'+'\t'+'Sample Type'+'\t'+'Analysis Method'+'\t'+'Results Group 1'+'\t'+'Instrument Protocol 1'+'\n'
        content=""
        con=""
        global_cont=""
        l=[]
    
        for sample in v_sample:
            v_setup=sample.file_setup and sample.file_setup.set_up and sample.file_setup.set_up.name or ""
            l.append(v_setup)
            l_st=dict([(i,0) for i in l if i]).keys()
            res=""
            i=1
            for k in l_st:
                res+=k+"+"
        res=res[0:len(res)-1]
        file_name=str(res)+'.csv'
        gg=""
        c=str(data['form']['container_a'] or "" )
        k=(data['form']['container_a'] or "")
        fields3= header_1 + str(res)+'\t'+""+'\t'+ str(data['form']['container_a'] or "") +'\t'+'Regular' +'\t'+ str(data['form']['owner_a'] or "")+'\t'+str(data['form']['operator_a'] or "")+'\t'+'\n'+header_2
        v_req=sample.sample_id and sample.sample_id.type_id and sample.sample_id.type_id.code or ''
        content=''
        t=[]
        for sample in v_sample:
        #    data_sample= str(sample.num_alpha)+'\t'+str(sample.progenus_number)+'\t'+"comment"+'\t'+str(100)+'\t'+"Size standard"+'\t'+"snp set"+'\t'+"UD3"+'\t'+"UD2"+'\t'+"UD1"+'\t'+'Panel'+'\t'+'Study'+'\t'+'CHECK IR'+'\t'+"METOD"+'\t'+"RES GRP1"+'\t'+str(v_req)+'\n'
            if view_type!='EMPDOG' and view_type!='EMPDOG_2' and view_type!='EMPCHE':
                data_sample= str(sample.num_alpha or "")+'\t'+str(sample.progenus_number or "")+'\t'+"comment"+'\t'+str(100)+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+''+'\t'+''+'\t'+''+'\t'+""+'\t'+""+'\t'+str(v_req)+'\n'
                content+=data_sample

            elif view_type=='EMPDOG' or view_type=='EMPCHE':
                if sample.dog_child and sample.dog_child.progenus_number and  sample.dog_child.progenus_number not in t:
                    data_sample_child= str(sample.dog_child and sample.dog_child.num_alpha or "")+'\t'+str(sample.dog_child and sample.dog_child.progenus_number or "")+'\t'+"comment"+'\t'+str(100)+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+''+'\t'+''+'\t'+''+'\t'+""+'\t'+""+'\t'+str(v_req)+'\n'
                    content+=data_sample_child
                    t.append(sample.dog_child.progenus_number)

                if sample.dog_mother and sample.dog_mother.progenus_number and  sample.dog_mother.progenus_number not in t:
                    data_sample_mother= str(sample.dog_mother and sample.dog_mother.num_alpha or "")+'\t'+str(sample.dog_mother and sample.dog_mother.progenus_number or "")+'\t'+"comment"+'\t'+str(100)+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+''+'\t'+''+'\t'+''+'\t'+""+'\t'+""+'\t'+str(v_req)+'\n'
                    content+=data_sample_mother
                    t.append(sample.dog_mother.progenus_number)

                if sample.dog_father and sample.dog_father.progenus_number and  sample.dog_father.progenus_number not in t:
                    data_sample_father= str(sample.dog_father and sample.dog_father.num_alpha or "")+'\t'+str(sample.dog_father and sample.dog_father.progenus_number or "")+'\t'+"comment"+'\t'+str(100)+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+''+'\t'+''+'\t'+''+'\t'+""+'\t'+""+'\t'+str(v_req)+'\n'
                    content+=data_sample_father
                    t.append(sample.dog_father.progenus_number)

            elif view_type=='EMPDOG_2':

                if sample.dog_mother and sample.dog_mother.progenus_number and  sample.dog_mother.progenus_number not in t:
                    data_sample_mother= str(sample.dog_mother and sample.dog_mother.num_alpha or "")+'\t'+str(sample.dog_mother and sample.dog_mother.progenus_number or "")+'\t'+"comment"+'\t'+str(100)+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+''+'\t'+''+'\t'+''+'\t'+""+'\t'+""+'\t'+str(v_req)+'\n'
                    content+=data_sample_mother
                    t.append(sample.dog_mother.progenus_number)

                if sample.dog_father and sample.dog_father.progenus_number and  sample.dog_father.progenus_number not in t:
                    data_sample_father= str(sample.dog_father and sample.dog_father.num_alpha or "")+'\t'+str(sample.dog_father and sample.dog_father.progenus_number or "")+'\t'+"comment"+'\t'+str(100)+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+""+'\t'+''+'\t'+''+'\t'+''+'\t'+""+'\t'+""+'\t'+str(v_req)+'\n'
                    content+=data_sample_father
                    t.append(sample.dog_father.progenus_number)

        out=base64.encodestring(fields3+content)
        return {'data': out , 'file_name':file_name}
    
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _attach_form, 'fields': _attach_fields, 'state':[('end','Cancel'), ('done','Create')]}
        },
        'done': {
            'actions': [_create_file],
            'result': {'type': 'state', 'state':'end'}
        }
    }
    fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
        'file_name':{'string':'File Name', 'type':'char'}
    }
    states={
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _attach_form, 'fields': _attach_fields, 'state':[('end','Cancel'), ('done','Create')]}
        },
        'done':{
            'actions': [_create_file],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
    }
create_file_machine('attach.machine')

