import netsvc
from osv import fields, osv
import pooler

class webmail_mail(osv.osv):
    _name="webmail.mail"
    _description="User Configuration"
    _columns={
        'user_id' : fields.many2one('res.users', 'User'),        
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
webmail_mail()