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
import time
import sys
if sys.version[0:3] > '2.4':
    from hashlib import md5
else:
    from md5 import md5


form = '''<?xml version="1.0"?>
<form string="Send Code">
    <field name="emailto" colspan="4"/>
</form>'''

fields = {
    'emailto': {'string': 'Email Address', 'required':True, 'size': 255 , 'type': 'char', 'help': 'Enter email on which address you want to get the Verifiation Code'}
}

class sendcode(wizard.interface):
    
    def send_code(self, cr, uid, data, context):
        
        key = md5(time.strftime('%Y-%m-%d %H:%M:%S') + data['form']['emailto']).hexdigest();
        
        smtpserver = pooler.get_pool(cr.dbname).get('email.smtpclient').browse(cr, uid, data['id'], context)
        state = smtpserver.test_verivy_email(cr, uid, [data['id']], data['form']['emailto'], code=key)
        if not state:
            raise Exception, 'Verification Failed, Please check the Server Configuration!!!'
        
        pooler.get_pool(cr.dbname).get('email.smtpclient').write(cr, uid, [data['id']], {'state':'waiting', 'code':key})
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

