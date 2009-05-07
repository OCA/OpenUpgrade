# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#import pygtk
#pygtk.require('2.0')
#import gtk
import os
import StringIO
import wizard
import netsvc
import time
import pooler
from mx  import DateTime
import base64


data_form = '''<?xml version="1.0"?>
<form string="Export Intrastat Data">
    <separator string="Export Intrastat Data into SDV format" colspan="4"/>
    <field name="type" />
</form>'''
form_fields = {
    'type' : {
        'string':'Type',
        'type':'selection',
        'required':False,
        'selection':[('export','Export'),('import','Import')],
    }

}
success_form = '''<?xml version="1.0"?>
<form string="Success">
    <separator string="Your Data is Exported, Please save file with .SDV extension" colspan="4"/>
    <field name="export_intrastat"/>
    <field name="note" colspan="4" nolabel="1"/>
    <newline/>
    <separator string="Note" colspan="4"/>
    <label string="The file name must be composed as follows : PPMMXXXX.SDV" colspan="4"/>
    <label string="'PP' represents the statistical regime (19 for arrivals or 29 for dispatches), 'MM' represents the month and 'XXXX' are four free-choice positions." colspan="4"/>

</form>'''

export_fields = {
    'export_intrastat' : {
        'string':'Export File',
        'type':'binary',
        'required':False,
        'readonly':True,
    },
    'note' : {'string':'Log','type':'text','readonly':True,},
}


#Intrastat Data : Export in SDV format
def c_ljust(s, size):
    """
    check before calling ljust
    """
    s= s or ''
    if type(s) in (int,float):
        s=str(s).zfill(size)
    if len(s) > size:
        s= s[:size]
    s = s.ljust(size)
    return s

class record:
    def __init__(self,values):
        self.values=values
        self.fields=[]
        self.fixed_values={}
        self.init_local_context()
    def init_local_context(self):
        raise 'Not implementted'
    def generate(self):
        res=''
        for (field_name,field_size) in self.fields:
            if field_name == 'FILLER':
                if field_size > 1:
                    value='0'*field_size
                else:
                    value=''
            elif field_name in self.fixed_values:
                value=self.fixed_values[field_name]
            elif field_name in self.values:
                value=self.values[field_name]
            else:
                continue
            res+=c_ljust(value,field_size)
        return res

class record_SDV(record):
    def init_local_context(self):
        self.fields=[
             ('ASCLNE',155),
             ('DCLRANT',10),
             ('ETAB',2),
             ('ATSEC',1),
             ('DCLRANT3',19),
             ('ISO3',2),
             ('BTW3',12),
             ('PCODE3',5),
             ('RETNR',8),
             ('ITNR',5),
             ('MSGFCT',1),
             ('DCLDATE',6),
             ('DCLYR',2),
             ('DCLMNTH',2),
             ('DCLDAY',2),
             ('PERDE',4),
             ('YEAR',2),
             ('MNTH',2),
             ('FLOW',1),
             ('STPROC',2),
             ('CTRYPT',2),
             ('FILLER',1),
             ('CTRYOR',2),
             ('FILLER',1),
             ('TPT',1),
             ('PORT',1),
             ('NAT',2),
             ('FILLER',1),
             ('CONTNR',1),
             ('TRXTYP1',1),
             ('TRXTYP2',1),
             ('BNL',8),
             ('TARN',2),
             ('NET',10),
             ('ADUN',10),
             ('VAL',10),
             ('AUT',10),
             ('EXTNR',13),
             ('INCOTERM',3),
             ('REGION',1),
             ('FILLER',8),
             ('CODEMON',3),
             ('FILLER',5)

        ]
        self.fixed_values={
           'ETAB':'00',
           'ATSEC':'0',
           'MSGFCT':'1',
           'DCLDATE':time.strftime('%y%m%d'),
           'STPROC':'00',
           'CTRYOR':'',
           'PORT':'0',
           'NAT':'',
           'CONTNR':'0',
           'TRXTYP1':'1',
           'TRXTYP2':'0',
           'TARN':'00',
           'AUT':'0000000000',
       }
def export_file(self, cr, uid, datas, context):
    recs=pooler.get_pool(cr.dbname).get('report.intrastat').browse(cr,uid,datas['ids'])
    export_line=''
    line_count=0
    for rec in recs:
        if not rec.intrastat_id:
            continue
        if rec['type']==datas['form']['type']:
            line_count+=1
            val={}
            val['DCLRANT']='0425003223' # fixed with panimpex Enterprice number
            val['DCLRANT3']='' # fixed with ''
            val['ITNR']=line_count
            val['PERDE']=rec['name']['code']
            val['FLOW']=rec['type']=='import' and "A" or "D"
            val['RETNR']=time.strftime('%Y%m')
            val['RETNR']=rec['type']=='import' and val['RETNR']+'19' or val['RETNR']+'29'
            val['CTRYPT']=rec['code']
            val['TPT']='0' # fixed with 0 .this is for 'Extended' declaration, and Panimpex use only 'Standard' declaration
            val['BNL']=rec['intrastat_id']['name']
            val['NET']=int(round(rec['weight']))
            val['ADUN']=int(round(rec['supply_units']))
            val['VAL']= int(round(rec['value']))
            val['EXTNR']=rec['ref']
            val['INCOTERM']='' #  this is for 'Extended' declaration, and Panimpex use only 'Standard' declaration
            val['REGION']=1 # This will always be '1' because Panimpex is located in Flanders, so when they export, it will come from Flanders, and when they import, it will arrive in Fanders too.
            val['CODEMON']=rec['currency_id']['code']

            export_line+=record_SDV(val).generate()+'\n'

    log="Successfully Exported\n\nSummary:\nTotal Intrastat lines : %d \n"\
            %(line_count)
    log_id=pooler.get_pool(cr.dbname).get('report.intrastat.export.log').create \
        (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'note':log,'name':datas['form']['type'],'nbr':line_count,'user_id' : uid},context=None)

    return {'note':log,'export_intrastat': base64.encodestring(export_line)}

class wizard_export_intrastat_data(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch' : data_form, 'fields' :form_fields, 'state':[('end','Cancel'),('save','Export')]}
        },
        'save': {
            'actions': [export_file],
            'result': {'type': 'form', 'arch' : success_form, 'fields' : export_fields, 'state':[('end','OK')]}
        },
    }
wizard_export_intrastat_data('electronic.report.intrastat.export.data')
