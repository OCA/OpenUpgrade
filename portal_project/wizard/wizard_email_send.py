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
import pooler

email_send_form = '''<?xml version="1.0"?>
<form string="Email Send">
    <field name="to"/>
    <newline/>
    <field name="subject"/>
    <newline/>
    <field name="body" />
</form>'''

email_send_fields = {
    'to': {'string':"Recipients", 'type':'many2many', 'relation':'res.users'},
    'subject': {'string':'Subject', 'type':'char', 'size':64, 'required':True},
    'body': {'string':'Message', 'type':'text_tag', 'required':True}
}

def _email_send(self, cr, uid, data, context):
    return {}

class email_send(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
        },
        'send': {
            'actions': [_email_send],
            'result': {'type': 'state', 'state':'end'}
        }
    }
email_send('portal.project.email.send')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
