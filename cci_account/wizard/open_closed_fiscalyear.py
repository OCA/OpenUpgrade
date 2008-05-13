import wizard
import netsvc
import pooler

from osv import fields, osv

form_msg = """<?xml version="1.0"?>
<form string="Inovoice Grouped">
    <field name="message"  colspan="5"/>
</form>
"""
fields_msg = {
      'message': {'string':'Entries Deleted', 'type':'text', 'readonly':True, 'size':'500'},
}

class open_closed_fiscal(wizard.interface):
    states = {
        'init' : {
               'actions' : [],
               'result': {'type': 'form', 'arch': form_msg, 'fields': fields_msg, 'state':[('end','Ok')]}
            },

    }
open_closed_fiscal("cci_account.open_closed_fiscal")