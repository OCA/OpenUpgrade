# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                    Jordi Esteve <jesteve@zikzakmedia.com>
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

import wizard
import pooler
import tools

from osv import fields,osv
import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict

email_send_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Send invoice/s by Email">
    <field name="to"/>
    <newline/>
    <field name="subject"/>
    <newline/>
    <separator colspan="4"/>
    <label string="Message:"/>
    <field name="text" nolabel="1" colspan="4"/>
</form>'''

email_send_fields = {
    'to': {'string':"To", 'type':'char', 'size':1024, 'required':True},
    'subject': {'string':'Subject', 'type':'char', 'size':64, 'required':True},
    'text': {'string':'Message', 'type':'text', 'required':True}
}

email_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Send invoice/s by Email">
    <field name="email_sent"/>
</form>'''

email_done_fields = {
    'email_sent': {'string':'Quantity of Emails sent', 'type':'integer', 'readonly': True},
}


def _get_defaults(self, cr, uid, data, context):
    p = pooler.get_pool(cr.dbname)
    user = p.get('res.users').browse(cr, uid, uid, context)
    subject = user.company_id.name+'. Num.'
    text = '\n--\n' + user.signature

    invoices = p.get(data['model']).browse(cr, uid, data['ids'], context)
    adr_ids = []
    partner_id = invoices[0].partner_id.id
    for inv in invoices:
        if partner_id != inv.partner_id.id:
            raise osv.except_osv('Warning', 'You have selected documents for different partners.')
        if inv.number:
            subject = subject + ' ' + inv.number
        if inv.name:
            text = inv.name + '\n' + text
        if inv.address_invoice_id.id not in adr_ids:
            adr_ids.append(inv.address_invoice_id.id)
        if inv.address_contact_id and inv.address_contact_id.id not in adr_ids:
            adr_ids.append(inv.address_contact_id.id)
    addresses = p.get('res.partner.address').browse(cr, uid, adr_ids, context)
    to = []
    for adr in addresses:
        if adr.email:
            name = adr.name or adr.partner_id.name
            # The adr.email field can contain several email addresses separated by ,
            to.extend(['%s <%s>' % (name, email) for email in adr.email.split(',')])
    to = ','.join(to)
    return {'to': to, 'subject': subject, 'text': text}


def _send_mails(self, cr, uid, data, context):
    import re
    p = pooler.get_pool(cr.dbname)

    user = p.get('res.users').browse(cr, uid, uid, context)
    file_name = user.company_id.name.replace(' ','_')+'_invoice'
    account_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','account'),('state','=','confirm')], context=False)
    if not account_smtpserver_id:
        default_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm')], context=False)
    smtpserver_id = account_smtpserver_id or default_smtpserver_id
    if not smtpserver_id:
        raise osv.except_osv('Error', 'No SMTP Server Defined!')
    smtpserver = p.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)[0]

    nbr = 0
    for email in data['form']['to'].split(','):
        print email, data['form']['subject'], data['ids'], data['form']['text'], data['model'], file_name
        state = smtpserver.send_email(cr, uid, smtpserver_id, email, data['form']['subject'], data['ids'], data['form']['text'], data['model'], file_name)
        if not state:
            raise osv.except_osv('Error sending email', 'Please check the Server Configuration!')
        nbr += 1

    # Add a partner event
    docs = p.get(data['model']).browse(cr, uid, data['ids'], context)
    partner_id = docs[0].partner_id.id
    c_id = p.get('res.partner.canal').search(cr ,uid, [('name','ilike','EMAIL'),('active','=',True)])
    c_id = c_id and c_id[0] or False
    p.get('res.partner.event').create(cr, uid,
            {'name': 'Email sent through invoice wizard',
             'partner_id': partner_id,
             'description': 'To: ' + data['form']['to'] + '\n\nSubject: ' + data['form']['subject'] + '\n\nText:\n' + data['form']['text'],
             'document': data['model']+','+str(docs[0].id),
             'canal_id': c_id,
             'user_id': uid, })
    return {'email_sent': nbr}


class send_email(wizard.interface):
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
        },
        'send': {
            'actions': [_send_mails],
            'result': {'type': 'form', 'arch': email_done_form, 'fields': email_done_fields, 'state': [('end', 'End')] }
        }
    }
send_email('account.invoice.email_send_2')
