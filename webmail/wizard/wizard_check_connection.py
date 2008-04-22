import wizard
import pooler

msg = ''

_message_form='''<?xml version="1.0"?>
<form string="Test Connection">
    <label string="%s" colspan="4" />
</form>'''  % (msg,)


def _message(self, cr, uid, data, context):
        msg = 'Connection successfully done'
        return 'message'

class wizard_check_connection(wizard.interface):     
    
    states = {
        'init': {
            'actions': [],
            'result':{'type' : 'choice', 'next_state':_message}
        },
        'message':{
                'actions':[],
                'result' : {'type':'form', 'arch':_message_form,'fields':{},'state':[('end','Exit')]}
        },       
    }
    
wizard_check_connection('webmail.check.connection')