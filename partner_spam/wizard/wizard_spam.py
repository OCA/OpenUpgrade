# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
# Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                    Jordi Esteve <jesteve@zikzakmedia.com>
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

import wizard
import pooler
import tools
import base64
import time

email_send_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Mass Mailing">
    <field name="smtp_server" colspan="4"/>
    <newline/>
    <field name="subject" colspan="4"/>

    <separator string="Message:" colspan="4"/>
    <field name="text" nolabel="1" colspan="4"/>

    <separator string="Attached files:" colspan="4"/>
    <field name="file1" filename="name1"/>
    <field name="name1"/>
    <field name="file2" filename="name2"/>
    <field name="name2"/>
    <field name="file3" filename="name3"/>
    <field name="name3"/>

    <separator string="Only send to addresses:" colspan="4"/>
    <group colspan="4" col="10">
        <field name="default"/>
        <field name="invoice"/>
        <field name="delivery"/>
        <field name="contact"/>
        <field name="other"/>
    </group>

    <separator string="The following tags can be included in the message. They will be replaced to the corresponding values of each partner contact:" colspan="4"/>
    <label string="[[partner_id]] -> Partner name" colspan="2"/>
    <label string="[[name]] -> Contact name" colspan="2"/>
    <label string="[[function]] -> Function" colspan="2"/>
    <label string="[[title]] -> Title" colspan="2"/>
    <label string="[[street]] -> Street" colspan="2"/>
    <label string="[[street2]] -> Street 2" colspan="2"/>
    <label string="[[zip]] -> Zip code" colspan="2"/>
    <label string="[[city]] -> City" colspan="2"/>
    <label string="[[state_id]] -> State" colspan="2"/>
    <label string="[[country_id]] -> Country" colspan="2"/>
    <label string="[[email]] -> Email" colspan="2"/>
    <label string="[[phone]] -> Phone" colspan="2"/>
    <label string="[[fax]] -> Fax" colspan="2"/>
    <label string="[[mobile]] -> Mobile" colspan="2"/>
    <label string="[[birthdate]] -> Birthday" colspan="2"/>
</form>'''

email_send_fields = {
    'smtp_server': {'string':"SMTP Server", 'type':'many2one', 'relation':'email.smtpclient', 'required':True},
    'subject': {'string':'Subject', 'type':'char', 'size':64, 'required':True},
    'default':  {'string':'Default', 'type':'boolean'},
    'invoice':  {'string':'Invoice', 'type':'boolean'},
    'delivery': {'string':'Delivery', 'type':'boolean'},
    'contact':  {'string':'Contact', 'type':'boolean'},
    'other':    {'string':'Other', 'type':'boolean'},
    'text': {'string':'Message', 'type':'text_tag', 'required':True},
    'name1': {'string':"File name 1", 'type':'char', 'size':64},
    'name2': {'string':"File name 2", 'type':'char', 'size':64},
    'name3': {'string':"File name 3", 'type':'char', 'size':64},
    'file1': {'string':'File 1', 'type':'binary'},
    'file2': {'string':'File 2', 'type':'binary'},
    'file3': {'string':'File 3', 'type':'binary'},
}

email_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Mass Mailing">
    <field name="email_sent"/>
</form>'''

email_done_fields = {
    'email_sent': {'string':'Quantity of Emails sent', 'type':'integer', 'readonly': True},
}


def _get_defaults(self, cr, uid, data, context):
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context)
    text = '\n--\n' + user.signature
    return {'text': text}


def attach_file(name, content):
    name = '/tmp/'+name
    try:
        fp = open(name, 'wb+');
        fp.write(content);
        fp.close();
    except Exception,e:
        print 'Exception in create report:',e
        return False
    return name


def _mass_mail_send(cr, uid, data, context, adr):
    import re
    # change the [[field]] tags with the partner address values
    pattern = re.compile('\[\[\S+\]\]')
    fields = pattern.findall(data['form']['text'])
    texts = []
    for field in fields:
        text = getattr(adr, field[2:-2])
        if text and field[-5:-2]=='_id': # State or country field
            text = text.name
        if text and field[2:-2]=='function': # functions field
            text = text.name
        texts.append(text and text.encode('utf-8') or '')
    mail = data['form']['text'].replace('%', '%%')
    mail = pattern.sub('%s', mail)
    mail = mail % tuple(texts)
    mail = mail.replace('%%', '%')
    #print mail

    # The adr.email field can contain several email addresses separated by ,
    name = adr.name or adr.partner_id.name
    to = ['%s <%s>' % (name, email) for email in adr.email.split(',')]
    #print to

    # List of attached files: List of tuples with (file_name, file_content)
    f_attach = []
    sufix = time.strftime("%d%m%y%H%M%S")
    if data['form']['file1']:
        f_attach.append(attach_file(data['form']['name1'] or 'file1_'+sufix, base64.decodestring(data['form']['file1'])))
    if data['form']['file2']:
        f_attach.append(attach_file(data['form']['name2'] or 'file2_'+sufix, base64.decodestring(data['form']['file2'])))
    if data['form']['file3']:
        f_attach.append(attach_file(data['form']['name3'] or 'file3_'+sufix, base64.decodestring(data['form']['file3'])))
    f_attach = [f for f in f_attach if f] # Removing False elements

    email_server = pooler.get_pool(cr.dbname).get('email.smtpclient')
    email_server.send_email(cr, uid, data['form']['smtp_server'], to, data['form']['subject'], mail, f_attach)

    # Add a partner event
    c_id = pooler.get_pool(cr.dbname).get('res.partner.canal').search(cr ,uid, [('name','ilike','EMAIL'),('active','=',True)])
    c_id = c_id and c_id[0] or False
    pooler.get_pool(cr.dbname).get('res.partner.event').create(cr, uid,
            {'name': 'Email sent to ' + ', '.join(to),
             'partner_id': adr.partner_id.id,
             'description': data['form']['subject'] + '\n\n' + mail,
             'canal_id': c_id,
             'user_id': uid, })
#TODO: log number of message sent


# this sends an email to ALL the addresses of the selected partners.
def _mass_mail_send_partner(self, cr, uid, data, context):
    nbr = 0
    address_obj = pooler.get_pool(cr.dbname).get('res.partner.address')
    adr_ids = []
    if not (data['form']['default'] or data['form']['invoice'] or data['form']['delivery'] or data['form']['contact'] or data['form']['other']): # All addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('partner_id','in',data['ids'])]))
    if data['form']['default']: # default addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('partner_id','in',data['ids']), ('type','=','default')]))
    if data['form']['invoice']: # invoice addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('partner_id','in',data['ids']), ('type','=','invoice')]))
    if data['form']['delivery']: # delivery addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('partner_id','in',data['ids']), ('type','=','delivery')]))
    if data['form']['contact']: # contact addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('partner_id','in',data['ids']), ('type','=','contact')]))
    if data['form']['other']: # other addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('partner_id','in',data['ids']), ('type','=','other')]))
    addresses = address_obj.browse(cr, uid, adr_ids, context)
    for adr in addresses:
        if adr.email:
            _mass_mail_send(cr, uid, data, context, adr)
            nbr += 1
    return {'email_sent': nbr}

class part_email(wizard.interface):
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
        },
        'send': {
            'actions': [_mass_mail_send_partner],
            'result': {'type': 'form', 'arch': email_done_form, 'fields': email_done_fields, 'state': [('end', 'End')] }
        }
    }
part_email('res.partner.spam_send_2')


# this sends an email to ALL of the selected addresses.
def _mass_mail_send_partner_address(self, cr, uid, data, context):
    nbr = 0
    address_obj = pooler.get_pool(cr.dbname).get('res.partner.address')
    adr_ids = []
    if not (data['form']['default'] or data['form']['invoice'] or data['form']['delivery'] or data['form']['contact'] or data['form']['other']): # All addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('id','in',data['ids'])]))
    if data['form']['default']: # default addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('id','in',data['ids']), ('type','=','default')]))
    if data['form']['invoice']: # invoice addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('id','in',data['ids']), ('type','=','invoice')]))
    if data['form']['delivery']: # delivery addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('id','in',data['ids']), ('type','=','delivery')]))
    if data['form']['contact']: # contact addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('id','in',data['ids']), ('type','=','contact')]))
    if data['form']['other']: # other addresses
        adr_ids.extend(address_obj.search(cr ,uid, [('id','in',data['ids']), ('type','=','other')]))
    addresses = address_obj.browse(cr, uid, adr_ids, context)
    for adr in addresses:
        if adr.email:
            _mass_mail_send(cr, uid, data, context, adr)
            nbr += 1
    return {'email_sent': nbr}

class part_email_partner_address(wizard.interface):
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
        },
        'send': {
            'actions': [_mass_mail_send_partner_address],
            'result': {'type': 'form', 'arch': email_done_form, 'fields': email_done_fields, 'state': [('end', 'End')] }
        }
    }
part_email_partner_address('res.partner.address.spam_send')
