import netsvc
from osv import fields, osv
import pooler

class webmail_mailbox(osv.osv):
    _name="webmail.mailbox"
    _description="User Mailbox"
    _columns={
        'user_id' : fields.many2one('res.users', 'User'),        
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
webmail_mailbox()