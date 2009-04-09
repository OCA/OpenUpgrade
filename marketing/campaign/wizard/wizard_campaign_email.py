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
import netsvc

email_send_form = '''<?xml version="1.0"?>
<form string="Send an E-Mail">
    <separator string="Header" colspan="4"/>
    <field name="from"/>
    <field name="on_error"/>
    <newline/>
    <field name="subject" colspan="3"/>
    <newline/>
    <separator string="Email" colspan="4"/>
    <field name="body" colspan="3"/>
</form>'''

email_send_fields = {
    'from': {'string':'From', 'type':'char', 'required':True},
    'on_error': {'string':'Error Return To', 'type':'char', 'required':True},
    'subject': {'string':'Subject', 'type':'char', 'required':True},
    'body': {'string':'Email Message', 'type':'text', 'required':True}
}

def _email_send(self, cr, uid, data, context):
    service = netsvc.LocalService("object_proxy")
    res = service.execute(cr.dbname, uid, 'campaign.partner', 'read', data['ids'], ['partner_id'])
    partners_id = map(lambda r: r['partner_id'][0], res)
    form = data['form']
    nbr = service.execute(cr.dbname, uid, 'res.partner', 'email_send', partners_id, form['from'], form['subject'], form['body'], form['on_error'])
    return {'email_sent': nbr}

class part_email(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':email_send_form, 'fields':email_send_fields, 'state':[('end','Cancel'),('send','Send Email')]}
        },
        'send': {
            'actions': [_email_send],
            'result': {'type':'state', 'state':'end'}
        }
    }
part_email('campaign.partner.email_send')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

