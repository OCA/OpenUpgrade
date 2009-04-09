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

import pooler
import wizard

_arch_no_call = """<?xml version="1.0"?>
<form string="Open Partner Info">
    <label string="User not on the phone !"/>
</form>"""

_arch_no_partner = """<?xml version="1.0"?>
<form string="Open Partner Info">
    <label string="No partner defined for this phone number !"/>
</form>"""

def _find_partner(self,cr,uid,data,context):
    pool = pooler.get_pool(cr.dbname)
    phone_id = pool.get('asterisk.phone').search(cr, uid, [('user_id','=',uid)])
    if not phone_id:
        raise wizard.except_wizard('UserError', 'No IP Phone defined for your user %d !\nContact the administrator.' % (uid,))
    phone = pool.get('asterisk.phone').browse(cr, uid, phone_id[0])
    if not phone.current_callerid:
        return 'no_call'
    adr_ids = pool.get('res.partner.address').search(cr, uid, [('phone','=',phone.current_callerid)])
    if not adr_ids:
        return 'no_partner'
    return 'open'

def _open_partner(obj, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    phone_id = pool.get('asterisk.phone').search(cr, uid, [('user_id','=',uid)])
    phone = pool.get('asterisk.phone').browse(cr, uid, phone_id[0])
    adr_ids = pool.get('res.partner.address').search(cr, uid, [('phone','=',phone.current_callerid)])
    partner_id = pool.get('res.partner.address').browse(cr, uid, adr_ids[0]).partner_id.id
    result = {
        'res_id': partner_id,
        'name': 'Partner',
        'view_type':'form',
        'view_mode':'form,tree',
        'res_model':'res.partner',
        'view_id':False,
        'type':'ir.actions.act_window',
    }
    return result

def _create_partner(obj, cr, uid, data, context):
    return {
        'name': 'Partner',
        'view_type':'form',
        'view_mode':'form,tree',
        'res_model':'res.partner',
        'view_id':False,
        'type':'ir.actions.act_window',
    }

class partner_open(wizard.interface):
    states = {
        'init' : {
            'result': {'type' : 'choice', 'next_state': _find_partner}
        },
        'no_call': {
            'result': {
                'type':'form', 'fields':{},
                'arch':_arch_no_call,
                'state': [ ('end','Exit'),('init','Retry') ]
            }
        },
        'no_partner': {
            'result': {
                'type':'form', 'fields':{},
                'arch':_arch_no_partner,
                'state': [ ('end','Exit'),('create','Create a New Partner') ]
            }
        },
        'create': {
            'result': {
                'type':'action',
                'action': _create_partner,
                'state': 'end'
            }
        },
        'open': {
            'result': {
                'type':'action',
                'action': _open_partner,
                'state': 'end'
            }
        }
    }
partner_open('asterisk.partner.get')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

