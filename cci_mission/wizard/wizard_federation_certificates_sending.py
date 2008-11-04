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

def past_month():
    past_month = str(int(time.strftime('%m'))-1)
    if past_month == '0':
        past_month = '12'
    return past_month

def year_past_month():
    past_month_year = int(time.strftime('%Y'))
    if int(time.strftime('%m')) == 1:
        past_month_year = past_month_year - 1
    return past_month_year

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

param_form = """<?xml version="1.0"?>
<form string="Select Options">
    <field name="cert_type" colspan="3"/>
    <field name="month"     colspan="1"/>
    <field name="year"      colspan="1"/>
    <field name="canceled"  colspan="3"/>
    <field name="email_to"  colspan="3"/>
    <field name="email_rcp" colspan="3"/>
</form>"""

fields = {
    'cert_type': {'string' : 'Certificate Type', 'type' : 'many2one', 'required' : True, 'relation':'cci_missions.dossier_type' ,'required':True,'domain' :[('section', '=', 'certificate')] }, 
    'month':     {'string' : 'Month', 'type':'selection','selection': MONTHS ,'required': True,'default' : past_month()},
    'year':      {'string' : 'Year', 'type':'integer','size' : 4,'required': True,'default': year_past_month()},
    'canceled':  {'string' : 'include canceled certificates', 'type' : 'boolean', 'default' : lambda *a: True }, 
    'email_to':  {'string': 'Sending email', 'type':'char', 'required': True,'size':128 ,'help':'The e-mail address where to send the file', 'default': lambda *a: 'co.woa@taktik.be'},
    'email_rcp': {'string': 'Reception email', 'type':'char', 'required': True,'size':128 ,'help':'The e-mail address where receive the proof of receipt (usually yours)'},
   }

msg_form = """<?xml version="1.0"?>
<form string="Notification">
    <label string="E-mail with certificates has been sent successfully!" />
    <label string="You'll receive an acknowledge/error in a few minutes on the given mailbox.">
</form>"""

msg_fields = {}

def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class wizard_cert_fed_send(wizard.interface):

    _field_separator  = chr(124)
    _record_separator = '\n\b'

    def make_lines(self,cr,uid,res_file, data):
        lines=[]
        
        # first header line : _field_separator + _record_separator + _field_separator
        # so the receiver can detect which separators we use
        lines.append( self._field_separator + self._record_separator + self._field_separator)
        
        # second header line : give the id code of the CCI, the number of details lines and the email address
        # for the sending of the reception of this file by the federation mail robot
        
        # we obtain the id key of the CCI in the federation
        res_company = self.pool.get('res.company')
        lines.append( res_company.federation_key + self._field_separator + str(len(res_file)).rjust(6,'0') + self._field_separator + str(data['form']['email_rcp']).strip() + self._field_separator )
        
        # Let's build a list of certificates objects
        certificates_ids = [x[0] for x in res_file]
        obj_certificate = pooler.get_pool(cr.dbname).get('cci_missions.certificate')
        certificates = obj_certificate.browse(cr,uid,certificates_ids)

        # create of list of value, then concatenate them with _field_separator for each certificate
        sequence_num = 0
        total_value = 0
        for certificate in certificates:
            fields = []
            sequence_num += 1

            fields.append( str(sequence_num).rjust(6,'0') )
            fields.append( certificate.type_id.id_letter + certificate.name.rpartition('/')[2].rjust(6,'0') )  # extract the right part of the number of the certificate (CO/2008/25 -> '25' the left justify with '0' -> '000025' )
            fields.append( certificate.dossier_id.asker_name )
            fields.append( certificate.asker_address )
            fields.append( certificate.asker_zip_id.name )
            fields.append( certificate.asker_zip_id.city )
            fields.append( certificate.dossier_id.sender_name )
            fields.append( certificate.dossier_id.destination_id.code )
            fields.append( str( int( certificate.dossier_id.goods_value * 100 )) ) # to have the value in cents, without , or .
            total_value += int( certificate.dossier_id.goods_value * 100 ) # I do this now, because, if I do this just before lines.append, i've got a bug !! If someone has an explanatio, I'm ready
            fields.append( certificate.dossier_id.date.replace('-','') )  # to correct '2008-05-28' to '20080528'
            fields.append( 'N' )
            custom_codes_string = ''
            for custom_code in certificate.customs_ids:
                custom_codes_string += custom_code.name + self._field_separator
            fields.append( custom_codes_string ) # YES, there will be TWO fields separators at the end of this list, to mark the end of the list, exactly
            origins_string = ''
            for country_code in certificate.origin_ids:
                origins_string += country_code.name + self._field_separator
            fields.append( origins_string ) # YES, there will be TWO fields separators at the end of this list, to mark the end of the list, exactly

            lines.append( self._field_separator.join(fields) + self._field_separator )
        
        # Trailer : the sum of all the values in cents of the included certificates
        lines.append( '999999' + self._field_separator + str( total_value ) + self._field_separator )

        # Since we send this file to the federation, we indicate this date in the field  
        # obj_certificate.write(cr, uid,certificates_ids, {'sending_spf' : time.strftime('%Y-%m-%d')})
        return lines

    def write_txt(self,name,lines):
        file=open(name, 'w')
        file.write(self._record_separator.join(lines))
        file.write(self._record_separator)
        file.close()

    def _send_mail(self, cr, uid, data, context):

        # Check of the first email address given by the user
        ptrn = re.compile('(\w+@\w+(?:\.\w+)+)')
        result=ptrn.search(data['form']['email_to'])
        if result==None:
            raise wizard.except_wizard('Error !', 'Enter Valid Destination E-Mail Address.')

        # Check of the first second email address given by the user
        ptrn = re.compile('(\w+@\w+(?:\.\w+)+)')
        result=ptrn.search(data['form']['email_rcp'])
        if result==None:
            raise wizard.except_wizard('Error !', 'Enter Valid Reception E-Mail Address.')

        # Determine the first and last date to select
        month=data['form']['month']
        year=int(data['form']['year'])
        self.first_day=datetime.date(year,int(month),1)
        self.last_day=datetime.date(year,int(month),lengthmonth(year, int(month)))
        period="to_date('" + self.first_day.strftime('%Y-%m-%d') + "','yyyy-mm-dd') and to_date('" + self.last_day.strftime('%Y-%m-%d') +"','yyyy-mm-dd')"

        #determine the type of certificates to send
        certificate_type = data['form']['cert_type']

        #Extraction of corresponding certificates
        cr.execute('select a.id from cci_missions_certificate as a, cci_missions_dossier as b where ( a.dossier_id = b.id ) and ( a.sending_spf is null ) and ( b.type_id = %s ) and ( b.date between %s )'%(certificate_type,period))
        res_file1=cr.fetchall()

        #If no records, cancel of the flow
        if res_file1==[]:
            raise wizard.except_wizard('Notification !', 'No Records Found to be sended. Check your criteria.')

        lines=[]
        root_path=tools.config.options['root_path']
        if res_file1:
            lines=self.make_lines(cr, uid, res_file1, data )
            self.write_txt(root_path+'/certificates.txt',lines)

        # Sending of the file as attachment
        files_attached=[]
        file1=tools.file_open(root_path+'/certificates.txt','rb',subdir=None)
        files_attached=[('certificates.txt',file1.read())]

        src = tools.config.options['smtp_user']  # parametre quand on lance le server ou dans bin\tools\config.py
        dest = [data['form']['email_to']]
        body = "Hello,\nHere are the certificates files for Federation.\nThink Big Use Tiny."
        tools.email_send_attach(src,dest,"Federation Sending Files From TinyERP",body,attach=files_attached)
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':param_form, 'fields':fields, 'state':[('end','Cancel'),('send','Send certificates')]},
        },
        'send': {
            'actions': [_send_mail],
            'result': {'type':'form', 'arch':msg_form, 'fields':msg_fields, 'state':[('end','Ok')]}
        },
    }

wizard_cert_fed_send('cci_mission.send_certificates_federation')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

