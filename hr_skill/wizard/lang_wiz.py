# -*- encoding: utf-8 -*-
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

