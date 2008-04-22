import wizard
import pooler

def _action_open_mail_account(self, cr, uid, data, context):    
    if data['ids'].__len__()>1:
        raise wizard.except_wizard('Error!', 'Please select only one mail account')    
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')    
    
    return {
        'domain': "[('user_id','=',%d)]" % (uid),
        'name': 'Mail Account',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'webmail.mailbox',
        'view_id': False,
        'context': "{}",
        'type': 'ir.actions.act_window'
    }

class wizard_mail_account(wizard.interface):
   
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_mail_account, 'state':'end'}
        },        
    }
    
wizard_mail_account('webmail.mail.account')