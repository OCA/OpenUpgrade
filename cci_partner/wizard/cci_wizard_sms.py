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
import tools
import pooler

sms_send_form = '''<?xml version="1.0"?>
<form string="%s">
    <separator string="%s" colspan="4"/>
    <field name="app_id"/>
    <newline/>
    <field name="user"/>
    <field name="password"/>
    <newline/>
    <field name="text" colspan="4"/>
    <newline/>
    <field name="event"/>

</form>''' % ('SMS - Gateway: clickatell','Bulk SMS send')

sms_send_fields = {
    'app_id': {'string':'API ID', 'type':'char', 'required':True},
    'user': {'string':'Login', 'type':'char', 'required':True},
    'password': {'string':'Password', 'type':'char', 'required':True},
    'text': {'string':'SMS Message', 'type':'text', 'required':True},
    'event': {'string':'Open Partners for Event History', 'type':'boolean'},
}

form1 = '''<?xml version="1.0"?>
<form string="SMS">
    <field name="nbr"/>
</form>'''

fields1 = {
    'nbr': {'string':"Number of sms sent", 'type':'char', 'size':64 , 'readonly':True},
}
def _sms_send(self, cr, uid, data, context):
    service = netsvc.LocalService("object_proxy")

    res_ids = service.execute(cr.dbname, uid, 'res.partner.address', 'search', [('partner_id','in',data['ids']),('type','=','default')])
    res = service.execute(cr.dbname, uid, 'res.partner.address', 'read', res_ids, ['mobile'])

    nbr = 0
    for r in res:
        to = r['mobile']
        if to:
            tools.sms_send(data['form']['user'], data['form']['password'], data['form']['app_id'], unicode(data['form']['text'], 'utf-8').encode('latin1'), to)
            nbr += 1

    data['form']['nbr'] = nbr
    if data['form']['event']:
        return 'open'
    return 'ok'

def _nbr_sms(self, cr, uid, data, context):
    return {'nbr':str(data['form']['nbr'])}

class part_sms(wizard.interface):
     def _open_partners(self, cr, uid, data, context):
         pool_obj = pooler.get_pool(cr.dbname)
         model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_partner_form')])
         resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
         return {
            'domain': "[('id','in', ["+','.join(map(str,data['ids']))+"])]",
            'name': 'Partners',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'views': [(False,'tree'),(resource_id,'form')],
            'type': 'ir.actions.act_window'
        }
     states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':sms_send_form, 'fields': sms_send_fields, 'state':[('end','Cancel'), ('send','Send SMS')]}
        },
        'send': {
            'actions': [],
            'result' : {'type': 'choice', 'next_state': _sms_send }
        },
         'ok':{
          'actions': [_nbr_sms],
         'result': {'type': 'form', 'arch': form1, 'fields': fields1, 'state':[('end','Ok')]}
              },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_partners, 'state':'end'}
                }
    }
part_sms('res.partner.sms_send_cci')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

