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
from osv import osv
import time
import sys

form = '''<?xml version="1.0"?>
<form string="Send Code">
    <field name="emailto" colspan="4"/>
</form>'''

fields = {
    'emailto': {'string': 'Email Address', 'required':True, 'size': 255 , 'type': 'char', 'help': 'Enter the address Email where you want to get the Verification Code'}
}

class sendcode(wizard.interface):

    def send_code(self, cr, uid, data, context):
        state = pooler.get_pool(cr.dbname).get('email.smtpclient').test_verify_email(cr, uid, [data['id']], data['form']['emailto'])
        if not state:
            raise osv.except_osv(_('Error'), _('Verification Failed. Please check the Server Configuration!'))

        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('send','Send Code')]}
        },
        'send': {
            'actions': [send_code],
            'result': {'type':'state', 'state':'end'}
        }
    }
sendcode('email.sendcode')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

