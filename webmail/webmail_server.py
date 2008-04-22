import netsvc
from osv import fields, osv
import pooler

class webmail_tiny_user(osv.osv):
    _name="webmail.tiny.user"
    _description="User Configuration"
    _columns={
        'user_id' : fields.many2one('res.users', 'User'),
        'server_conf_id':fields.one2many('webmail.server','server_id','Configuration')
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
webmail_tiny_user()

class webmail_server(osv.osv):
    _name="webmail.server"
    _description="Mail Server Configuration"
    _columns={
        'name' : fields.char("Name", size=64, required=True),
        'iserver_name' : fields.char('Server Name', size=64, required=True),
        'iserver_type' : fields.selection([('imap','IMAP'),('pop3','POP3')], 'Server Type'),
        'iuser_name':fields.char('User Name', size=64, required=True),
        'ipassword':fields.char('Password', size=64, required=True),
        'iconn_type':fields.selection([('tls','TLS'),('ssl','SSL')],'Connection Type'),
        'iconn_port':fields.integer('Port'),
        'oserver_name' : fields.char('Server Name', size=64, required=True),
        'ouser_name':fields.char('User Name', size=64, required=True),
        'opassword':fields.char('Password', size=64, required=True),
        'oconn_type':fields.selection([('tls','TLS'),('ssl','SSL')],'Connection Type'),
        'oconn_port':fields.integer('Port'),
        'server_id':fields.many2one('webmail.tiny.user',"Mail Client"),
    }
    _default={
        'oconn_port': lambda *a: 25,
    }
webmail_server()