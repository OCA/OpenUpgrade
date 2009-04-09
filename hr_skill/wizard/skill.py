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

emp_form = '''<?xml version="1.0"?>
<form string="Select period">
        <field name="s_ids"/>
</form>'''

emp_field ={
    's_ids': {'name' : 'skill', 'relation':'hr_skill.skill', 'string':'Skill', 'required':'True', 'type':'many2one','domain':"[('view','=','skill')]"},
   }

class skillemployee(wizard.interface):
    states = {
       'init': {
                    'actions': [],
                    'result': {'type':'form', 'arch':emp_form, 'fields':emp_field, 'state':[('end','Cancel'),('report','Print')]}
        },

       'report': {
                    'actions': [],
                    'result': {'type':'print', 'report':'skillreport', 'state':'end'}
        }
    }

skillemployee('empskill')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

