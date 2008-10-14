# -*- encoding: utf-8 -*-
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

