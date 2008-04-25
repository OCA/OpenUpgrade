import wizard
import pooler

def _action_open_mail_account(self, cr, uid, data, context):
    if data['form']['ids'].__len__()>1:
        raise wizard.except_wizard('Error!', 'Please select only one mail account')    
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')
    server_obj = pooler.get_pool(cr.dbname).get('webmail.server')
    
    folder_ids = mailbox_obj.search(cr, uid,[('user_id','=',uid)])
    mailbox_obj.unlink(cr, uid, folder_ids)
        
    acc_ids = server_obj.search(cr, uid,[('user_id','=',uid)])
    acc_data = server_obj.browse(cr, uid, acc_ids)
    
    for mail_acc in acc_data:
        parent_accid = mailbox_obj.create(cr, uid, {'name':mail_acc.name})
        if mail_acc.iconn_type=='imap':
            folders = server_obj._select(cr, uid, ids, context, mail_acc)
            for folder in folders:
                mailbox_obj.create(cr, uid, {'name':folder, 'parent_id':parent_accid})
        else:
            mailbox_obj.create(cr, uid, {'name':'Inbox', 'parent_id':parent_accid })        
        
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