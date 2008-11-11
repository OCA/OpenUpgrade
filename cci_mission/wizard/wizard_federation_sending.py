# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import wizard
import time
import datetime
import re
import tools
import pooler
import csv



MONTHS = [
    ('1', 'January'),
    ('2', 'February'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December')
]

form = """<?xml version="1.0"?>
<form string="Select Options">
    <field name="month" colspan="2"/>
    <field name="email" colspan="2"/>
</form>"""

fields = {
    'month': {'string': 'Month Duration for Closure Date', 'type':'selection','selection': MONTHS ,'required': True,'default':lambda *a: str(int(time.strftime('%m'))-1)},
    'email': {'string': 'E-mail Id', 'type':'char', 'required': True,'size':128 ,'help':'Write comma separated Ids if there are more than one receipents.e.g. name@domain1.com,name1@domain2.com'},
   }

msg_form = """<?xml version="1.0"?>
<form string="Notification">
    <label string="E-mail has been sent successfully!" />
</form>"""

msg_fields = {}

def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class wizard_fed_send(wizard.interface):

    def make_csv(self,cr,uid,res_file,file2):
        lines=[]
        carnet_ids=[x[0] for x in res_file]
        obj_carnet=pooler.get_pool(cr.dbname).get('cci_missions.ata_carnet')
        carnet_selected_ids=obj_carnet.browse(cr,uid,carnet_ids)

        for carnet_line in carnet_selected_ids:
            line_dict={}
            line_dict['Id']=carnet_line.id
            line_dict['Name']=carnet_line.name
            line_dict['Partner']=carnet_line.partner_id.name
            line_dict['Related Type of Carnet']=carnet_line.type_id.name
            line_dict['Emission Date']=carnet_line.creation_date
            line_dict['Validity Date']=carnet_line.validity_date
            line_dict['Holder Name']=carnet_line.holder_name
            line_dict['Holder Address']=carnet_line.holder_address
            line_dict['Holder City']=carnet_line.holder_city
            line_dict['Representer Name']=carnet_line.representer_name
            line_dict['Representer Address']=carnet_line.representer_address
            line_dict['Representer City']=carnet_line.representer_city
            line_dict['Usage']=carnet_line.usage_id.name
            line_dict['Goods']=carnet_line.goods
            line_dict['Area']=carnet_line.area_id.name
            line_dict['Insurer Agreement']=carnet_line.insurer_agreement
            line_dict['Own Risks']=carnet_line.own_risk
            line_dict['Goods Value']=carnet_line.goods_value
            line_dict['Double Signature']=carnet_line.double_signature
            line_dict['Initial No. of Pages']=carnet_line.initial_pages
            line_dict['Additional No. of Pages']=carnet_line.additional_pages
            line_dict['Warranty']=carnet_line.warranty
            line_dict['Related Warranty Product']=carnet_line.warranty_product_id.name
            line_dict['Date of Return']=carnet_line.return_date
            line_dict['State']=carnet_line.state
            line_dict['Date of Closure']=carnet_line.ok_state_date
            line_dict['Date of Sending to the Federation']=carnet_line.federation_sending_date
            line_dict['Apply the Member Price']=carnet_line.member_price

            lines.append(line_dict)
        obj_carnet.write(cr, uid,carnet_ids, {'federation_sending_date' : time.strftime('%Y-%m-%d')})
        if file2==1:
            vals={}
            vals['state']='correct'
            vals['ok_state_date']=self.last_day.strftime('%Y-%m-%d')
            obj_carnet.write(cr, uid,carnet_ids,vals)
        return lines

    def write_csv(self,name,fields,lines):
        file=open(name, 'w')
        file.write(','.join(fields)+"\n")
        w=csv.DictWriter(file, fields, extrasaction='ignore')
        line_list=lines
        for line in line_list:
            w.writerow(line)
        file.close()

    def _send_mail(self, cr, uid, data, context):

        ptrn = re.compile('(\w+@\w+(?:\.\w+)+)')
        result=ptrn.search(data['form']['email'])
        if result==None:
            raise wizard.except_wizard('Error !', 'Enter Valid E-Mail Address.')

        fields=['Id','Name','Partner','Related Type of Carnet','Emission Date','Validity Date','Holder Name','Holder Address','Holder City','Representer Name','Representer Address','Representer City','Usage','Goods','Area','Insurer Agreement','Own Risks','Goods Value','Double Signature','Initial No. of Pages','Additional No. of Pages','Warranty','Related Warranty Product','Date of Return','State','Date of Closure','Date of Sending to the Federation','Apply the Member Price']
        # For First CSV

        month=data['form']['month']
        yr=int(time.strftime('%Y'))
        self.first_day=datetime.date(yr,int(month),1)
        self.last_day=datetime.date(yr,int(month),lengthmonth(yr, int(month)))

        period="to_date('" + self.first_day.strftime('%Y-%m-%d') + "','yyyy-mm-dd') and to_date('" + self.last_day.strftime('%Y-%m-%d') +"','yyyy-mm-dd')"

        cr.execute('select id from cci_missions_ata_carnet where federation_sending_date is  null and ok_state_date between %s'%(period))
        res_file1=cr.fetchall()
        lines=[]
        root_path=tools.config.options['root_path']
        if res_file1:
            lines=self.make_csv(cr, uid,res_file1,file2=0)
            self.write_csv(root_path+'/carnet_1.csv',fields,lines)
        # First CSV created
        # Process for second CSV -Start
        today=datetime.datetime.today()
        _date=datetime.date(today.year-2,today.month,today.day)
        comp_date=_date.strftime('%Y-%m-%d')
        cr.execute('select id from cci_missions_ata_carnet where federation_sending_date is  null and state='"'pending'"' and return_date <='"'%s'"''%(str(comp_date)))
        res_file2=cr.fetchall()
        lines=[]
        if res_file2:
            lines=self.make_csv(cr, uid,res_file2,file2=1)
            self.write_csv(root_path+'/carnet_2.csv',fields,lines)
        # Second CSV created.
        if res_file1==[] and res_file2==[]:
            raise wizard.except_wizard('Notification !', 'No Records Found to make the CSV files.Choose other criteria.')
        files_attached=[]

        if res_file1:
            file_csv1=tools.file_open(root_path+'/carnet_1.csv','rb',subdir=None)
            files_attached=[('Ata_carnet_csv_1.csv',file_csv1.read())]
        if res_file2:
            file_csv2=tools.file_open(root_path+'/carnet_2.csv','rb',subdir=None)
            files_attached.append(('Ata_carnet_csv_2.csv',file_csv2.read()))

        src=tools.config.options['smtp_user']
        dest=[data['form']['email']]
        body="Hello,\nHere are the CSV files for Federation Sending.\nThanks You For Using TinyERP.\nThink Big Use Tiny."
        tools.email_send_attach(src,dest,"Federation Sending Files From TinyERP",body,attach=files_attached)
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('send','Send E-Mail')]},
        },
        'send': {
            'actions': [_send_mail],
            'result': {'type':'form', 'arch':msg_form, 'fields':msg_fields, 'state':[('end','Ok')]}
        },
    }

wizard_fed_send('mission.fed_send')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

