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
import pooler
import tools
import base64

sent_dict = {}
not_sent = []

mail_send_form = '''<?xml version="1.0"?>
<form string="Mail to Customer">
    <field name="partner_id"/>
    <newline/>
    <field name="subject"/>
    <newline/>
    <field name="message"/>
    <newline/>
    <field name ="attachment"/>
</form>'''

mail_send_fields = {
    'partner_id': {'string': 'Customer','type': 'many2many', 'relation': 'ecommerce.partner'},
    'subject': {'string': 'Subject', 'type': 'char', 'size': 64, 'required': True},
    'message': {'string': 'Message', 'type': 'text', 'required': True},
    'attachment': {'string': 'Attachment', 'type': 'many2one', 'relation': 'ir.attachment'}
}
   
finished_form = '''<?xml version="1.0"?>
    <form string="Mail send">
        <label string="Operation Completed" colspan="4"/>
        <field name="mailsent" width="300"/>
        <field name="mailnotsent" width="300"/>
    </form>'''

finished_fields = {
    'mailsent': {'string': 'Mail Sent to', 'type': 'text'},
    'mailnotsent': {'string': 'Mail Not sent', 'type': 'text'}
}

class ecommerce_sendmail_wizard(wizard.interface):
 
    def _send_reminder(self, cr, uid, data, context):

        partner = data['form']['partner_id'][0][2]
        if partner:
            res = pooler.get_pool(cr.dbname).get('ecommerce.partner').browse(cr, uid, partner)
            for partner in res:
                if partner.address_ids and not partner.address_ids[0].email:
                    not_sent.append(partner.name)
                    for adr in partner.address_ids:
                        if adr.email:
                            sent_dict[partner.name] = adr.email
                            name = adr.username or partner.name
                            to = '%s <%s>' % (name, adr.email)
                            mail_from = 'priteshmodi.eiffel@yahoo.co.in'
                           
                            attach_ids = pooler.get_pool(cr.dbname).get('ir.attachment').search(cr, uid, 
                                                                                                [('res_model', '=', 'ecommerce.shop'),
                                                                                                ('res_id', '=', data['ids'][0])])
                            res_atc = pooler.get_pool(cr.dbname).get('ir.attachment').read(cr, uid,
                                                                                           attach_ids, ['datas_fname', 'datas'])
                            res_atc = map(lambda x: (x['datas_fname'],
                                                     base64.decodestring(x['datas'])), res_atc)
                            tools.email_send(mail_from, [to], data['form']['subject'], data['form']['message'], attach=res_atc)

        return 'finished'

    def get_mail_dtl(self, cr, uid, data, context):
        cust_get_mail = []
        cust_not_get_mail = []
        mail_value = ''
        not_mail = ''
        for items in sent_dict:
            cust_get_mail.append(items) 
            mail_value = mail_value + ',' + items
            
        for items_not in not_sent:
            cust_not_get_mail.append(items_not)
            not_mail = not_mail + ',' + items_not
            
        return {'mailsent': str(mail_value), 'mailnotsent': str(not_mail)}

    states = {
        'init': {
                'actions': [],
                'result': {'type': 'form', 'arch': mail_send_form, 'fields': mail_send_fields, 'state': [('end', 'Cancel'), ('connect', 'Send Mail')]}
        },
        'connect': {
                'actions': [],
                'result': {'type':'choice', 'next_state': _send_reminder},
        },
        'finished': {
                'actions': [get_mail_dtl],
                'result': {'type': 'form', 'arch': finished_form, 'fields': finished_fields, 'state': [('end','OK')]}
        }
    }
  
ecommerce_sendmail_wizard('ecommerce.customer.sendmail') 


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

