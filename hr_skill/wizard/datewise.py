# -*- encoding: utf-8 -*-
import wizard
import pooler
import time


dates_form = '''<?xml version="1.0"?>
<form string="Select period">
        <field name="sdate"/>
        <newline/>
        <field name="edate"/>
</form>'''

dates_fields ={
    'sdate': {'string':'Start Date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-01-01')},
    'edate': {'string':'End Date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
            }


class datewisecheck(wizard.interface):

    states = {
       'init': {
                    'actions': [],
                    'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
                    'actions': [],
                    'result': {'type':'print', 'report':'datereport.print', 'state':'end'}
        }
    }
datewisecheck('employee.date.check')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

