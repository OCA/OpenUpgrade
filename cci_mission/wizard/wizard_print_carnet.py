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
import time
import pooler


form = """<?xml version="1.0"?>
<form string="Select No. of Pages For Documents">
    <field name="pages_doc1"/>
    <field name="pages_doc2"/>
</form>"""

fields = {
    'pages_doc1': {'string': 'No. of pages in document1', 'type':'integer', 'required': True},
    'pages_doc2': {'string': 'No. of pages in document2', 'type':'integer', 'required': True},
   }

class wizard_report(wizard.interface):
    def _checkint(self, cr, uid, data, context):

        if data['form']['pages_doc1'] <0 or data['form']['pages_doc2']<0:
            raise wizard.except_wizard('Warning !', 'Please Enter Positive Values!')
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [_checkint],
            'result': {'type':'print', 'report':'cci_missions_print_carnet', 'state':'print1'},
        },
        'print1': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet1', 'state':'end'},
        },
    }

wizard_report('cci_missions_print_carnet')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

