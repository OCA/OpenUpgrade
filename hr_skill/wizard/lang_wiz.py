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
import netsvc
from tools.misc import UpdateableStr,UpdateableDict

info = '''<?xml version="1.0"?>
<form string="Select period">
    <label string="Select Language !"/>
</form>'''

form1 = '''<?xml version="1.0"?>
<form string="Select period">

    <field name="lang"/>

 </form>'''

field1 = {
    'lang': {'string':'Language', 'type':'one2many', 'relation':'emp.lang'},

        }

class lang_get(wizard.interface):
    states = {

       'init': {
            'actions': [],
            'result': {'type':'form','arch':form1, 'fields':field1, 'state':[('end','Cancel'),('rpt','Report')]}
        },

        'rpt': {
            'actions': [],
            'result': {'type':'print','report':'langreport','state':'end'}
                },

             }
lang_get('langget')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

