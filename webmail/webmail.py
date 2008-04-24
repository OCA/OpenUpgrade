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
        'name': fields.char("Name", size=64, required=True),
        'iserver_name': fields.char('Server Name', size=64, required=True),
        'iserver_type': fields.selection([('imap','IMAP'),('pop3','POP3')], 'Server Type'),
        'iuser_name':fields.char('User Name', size=64, required=True),
        'ipassword':fields.char('Password', size=64, required=True),
        'iconn_type':fields.selection([('tls','TLS'),('ssl','SSL')],'Connection Type'),
        'iconn_port':fields.integer('Port'),
        'oserver_name': fields.char('Server Name', size=64, required=True),
        'ouser_name':fields.char('User Name', size=64, required=True),
        'opassword':fields.char('Password', size=64, required=True),
        'oconn_type':fields.selection([('tls','TLS'),('ssl','SSL')],'Connection Type'),
        'oconn_port':fields.integer('Port'),
        'server_id':fields.many2one('webmail.tiny.user',"Mail Client"),
    }
    _default={
        'oconn_port': lambda *a: 25,
    }
    
    def _login(self, cr, uid, context, host, port, user, password, ssl, type):
        pass
    
webmail_server()

class webmail_mailbox(osv.osv):
    _name="webmail.mailbox"
    _description="User Mailbox"
    _columns={
        'user_id': fields.many2one('res.users', 'User'),
        'name': fields.char('Name', size=64, required=True),
        'parent_id': fields.many2one('webmail.mailbox','Parent Folder', select=True),
        'child_id': fields.one2many('webmail.mailbox', 'parent_id', string='Child Folder'),
        'account_id': fields.many2one('webmail.server', 'Server'),
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def _rename(self, cr, uid, context, old, new):
        pass
    
    def _new(self, cr, uid, context, name):
        pass
    
    def _delete(self, cr, uid, context, name):
        pass
    
webmail_mailbox()

class webmail_email(osv.osv):
    _name="webmail.email"
    _description="User Email"
    _columns={
        'user_id': fields.many2one('res.users', 'User'),
        'account_id': fields.many2one('webmail.server', 'User'),
        'folder_id': fields.many2one('webmail.mailbox', 'Folder'),
        'message_id': fields.char('Message Id',size=256),
        'active': fields.boolean('Active'),
        'from': fields.char('From', size=256),
        'to': fields.char('To', size=256),
        'subject': fields.char('Subject', size=256),
        'date': fields.datetime('Date'),
        'cc': fields.char('Cc', size=256),
        'bcc': fields.char('Bcc', size=256),
        'body': fields.text('Body'),
        'attachment_id': fields.one2many('webmail.email.attachment', 'email_id', string='Attachment'),
        'tag_id': fields.many2one('webmail.tags', 'Tags',domain=[('user_id','=',uid)]),
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def _send_mail(self, cr, uid, context):
        pass
    
webmail_email()

class webmail_email_attachment(osv.osv):
    _name="webmail.email.attachment"
    _description="Email Attachment"
    _rec_name="attachment"
    _columns={
        'user_id': fields.many2one('res.users', 'User'),
        'email_id': fields.many2one('webmail.email', 'Email'),
        'attachment': fields.binary('Attachment'),
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
webmail_email_attachment()

class webmail_tags(osv.osv):
    _name="webmail.tags"
    _description="Email Tag"
    _columns={
        'user_id': fields.many2one('res.users', 'User'),
        'name': fields.char('Tag Name', size=128),        
        'account_id': fields.many2one('webmail.server', 'Server'),
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
        'account_id': lambda obj, cr, uid, context: context.get('account_id',False),
    }
webmail_tags()
