import wizard
import pooler

def _action_open_mail_account(self, cr, uid, data, context):
    if data['ids'].__len__()>1:
        raise wizard.except_wizard('Error!', 'Please select only one mail account')
    user_obj = pooler.get_pool(cr.dbname).get('webmail.tiny.user')
    mailbox_obj = pooler.get_pool(cr.dbname).get('webmail.mailbox')
    server_obj = pooler.get_pool(cr.dbname).get('webmail.server')
    
    mailbox_ids = mailbox_obj.search(cr, uid,[('user_id','=',uid)])
    mailbox_obj.unlink(cr, uid, mailbox_ids)

    for server in user_obj.browse(cr, uid, data['ids'][0]).server_conf_id:
        mail_acc = server_obj.browse(cr, uid, server.id)
        parent_accid = mailbox_obj.create(cr, uid, {'name':mail_acc.name, 'user_id':uid })
        
        if mail_acc.iserver_type=='imap':        
                folders = mailbox_obj._select(cr, uid, data['ids'], context, mail_acc)
                for folder in folders:
                    name = folder.split('/')
                    if name.__len__()>0:
                        name = name[1]
                    else:
                        name = folder
                    mailbox_obj.create(cr, uid, {'name':name, 'parent_id':parent_accid, 'user_id':uid })
        elif mail_acc.iconn_type=='smtp':
            mailbox_obj.create(cr, uid, {'name':'Inbox', 'parent_id':parent_accid, 'user_id':uid })         
        
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