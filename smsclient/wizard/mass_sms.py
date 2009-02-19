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

import wizard
import netsvc
import tools
import pooler

sms_send_form = '''<?xml version="1.0"?>
<form string="SMS Gateway - Send SMS">
    <separator string="Gateway and Message Text" colspan="4"/>
    <field name="gateway"/>
    <field name="text" colspan="4"/>
</form>'''

sms_send_fields = {
    'gateway':{'string':'SMS Gateway', 'type':'many2one', 'relation':'sms.smsclient', 'required':True},
    'text': {'string':'SMS Message', 'type':'text', 'required':True}
}

def _sms_send(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    gateway = pool.get('sms.smsclient')
    service = netsvc.LocalService("object_proxy")

    res_ids = service.execute(cr.dbname, uid, 'res.partner.address', 'search', [('partner_id','in',data['ids']),('type','=','default')])
    res = service.execute(cr.dbname, uid, 'res.partner.address', 'read', res_ids, ['mobile'])
    
    nbr = 0
    for r in res:
        to = r['mobile']
        if to:
            gateway.send_message(cr, uid, data['form']['gateway'], to, data['form']['text'])
            nbr += 1
    
    return {'sms_sent': nbr}

class part_sms(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':sms_send_form, 'fields': sms_send_fields, 'state':[('end','Cancel'), ('send','Send SMS')]}
        },
        'send': {
            'actions': [_sms_send],
            'result': {'type': 'state', 'state':'end'}
        }
    }
part_sms('res.partner.sms_send.gateway')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

