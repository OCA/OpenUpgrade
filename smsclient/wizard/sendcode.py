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
if sys.version[0:3] > '2.4':
    from hashlib import md5
else:
    from md5 import md5


form = '''<?xml version="1.0"?>
<form string="Send Code">
    <field name="smsto" colspan="4"/>
</form>'''

fields = {
    'smsto': {'string': 'Mobile No', 'required':True, 'size': 12 , 'type': 'char', 'help': 'Enter the Mobile No on which you want to receive the Verification Code'}
}

class sendcode(wizard.interface):

    def send_code(self, cr, uid, data, context):
        key = md5(time.strftime('%Y-%m-%d %H:%M:%S') + data['form']['smsto']).hexdigest();
        sms_pool = pooler.get_pool(cr.dbname).get('sms.smsclient')
        gate = sms_pool.browse(cr, uid, data['id'])
        msg = key[0:6]
        sms_pool.send_message(cr, uid, data['id'], data['form']['smsto'], msg)
        if not gate.state in('new', 'waiting'):
            raise osv.except_osv(_('Error'), _('Verification Failed. Please check the Server Configuration!'))

        pooler.get_pool(cr.dbname).get('sms.smsclient').write(cr, uid, [data['id']], {'state':'waiting', 'code':msg})
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
sendcode('sms.smsclient.code.send')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

