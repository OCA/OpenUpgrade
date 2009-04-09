# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import netsvc
from osv import fields, osv
import pooler

import imaplib
import poplib
import smtplib

class webmail_tiny_user(osv.osv):
    _name="webmail.tiny.user"
    _description="User Configuration"
    _rec_name="user_id"
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
        'user_name':fields.char('User Name', size=64, required=True),
        'password':fields.char('Password', size=64, required=True, invisible=True),
        'iconn_type':fields.boolean('SSL'),        
        'iconn_port':fields.integer('Port'),
        'oserver_name': fields.char('Server Name', size=64, required=True),        
        'oconn_type':fields.boolean('SSL'),
        'oconn_port':fields.integer('Port'),
        'server_id':fields.many2one('webmail.tiny.user',"Mail Client"),
    }
    _default={
        'oconn_port': lambda *a: 25,
    }
    
    def login(self, cr, uid, ids, context, server, port, ssl, type, user, password):        
        obj = None
        try:
            if type=='imap':
                if ssl:
                    obj = imaplib.IMAP4_SSL(server, port)
                else:
                    obj = imaplib.IMAP4(server, port)
            elif type=='pop3':
                if ssl:
                    obj = poplib.POP3_SSL(server, port)
                else:
                    obj = poplib.POP3(server, port)
            elif type=='smtp':
                if ssl:
                    obj = smtplib.SMTP(server, port)
                else:
                    obj = smtplib.SMTP(server, port)
            obj.login(user, password)            
        except Exception,e:
            pass
        return obj
        
    def test_connection(self, cr, uid, ids, context):
        server = self.browse(cr, uid, ids[0])
        iobj = self.login(cr, uid, ids, context, server.iserver_name, server.iconn_port, server.iconn_type, server.iserver_type, server.user_name, server.password)
        oobj = self.login(cr, uid, ids, context, server.oserver_name, server.oconn_port, server.oconn_type, 'smtp', server.user_name, server.password)
        if not iobj and not oobj:
            raise osv.except_osv(
                        'Connection Error !',
                     'Please enter valid server information.')
        elif not iobj:
           raise osv.except_osv(
                        'Connection Error !',
                     'Please enter valid incoming server information.')
        elif not oobj:
            raise osv.except_osv(
                        'Connection Error !',
                     'Please enter valid outgoing server information.')
        else:
            raise osv.except_osv(
                        'Connection!',
                        'Connection done successfully.')        
        return True
        
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
    
    def select(self, cr, uid, ids, context, mail_acc):
        server_obj = pooler.get_pool(cr.dbname).get('webmail.server')
        obj = server_obj.login(cr, uid, ids, context, mail_acc.iserver_name, mail_acc.iconn_port, mail_acc.iconn_type, mail_acc.iserver_type, mail_acc.user_name, mail_acc.password)
        return obj.list()[1]
        
    def new(self, cr, uid, ids, context, name):
         mailbox_obj = self.pool.get('webmail.mailbox')
         server_obj = self.pool.get('webmail.server')
         
         mailbox = mailbox_obj.browse(cr, uid, ids[0])
         server = server_obj.browse(cr, uid, mailbox.account_id.id)
         if server.iserver_type=='imap':
             obj = server.login(cr, uid, ids, context, server.iserver_name, server.iconn_port, server.iconn_type, server.iserver_type, server.user_name, server.password)
             if obj:
                obj.create(name)
                mailbox_obj.create(cr, uid, {'name':name, 'parent_id':mailbox.parent_id})
    
    def rename(self, cr, uid, ids, context, old, new):
        mailbox_obj = self.pool.get('webmail.mailbox')
        server_obj = self.pool.get('webmail.server')
        
        mailbox = mailbox_obj.browse(cr, uid, ids[0])
        server = server_obj.browse(cr, uid, mailbox.account_id.id)
        if server.iserver_type=='imap':
            obj = server.login(cr, uid, ids, context, server.iserver_name, server.iconn_port, server.iconn_type, server.iserver_type, server.user_name, server.password)
            if obj:
                obj.rename(old, new)
                mailbox_obj.write(cr, uid, ids, {'name': new_name })    
    
    def delete(self, cr, uid, ids, context):
        mailbox_obj = self.pool.get('webmail.mailbox')
        server_obj = self.pool.get('webmail.server')
        
        mailbox = mailbox_obj.browse(cr, uid, ids[0])
        server = server_obj.browse(cr, uid, mailbox.account_id.id)
        if server.iserver_type=='imap':
            obj = server.login(cr, uid, ids, context, server.iserver_name, server.iconn_port, server.iconn_type, server.iserver_type, server.user_name, server.password)
            if obj:
                obj.delete(mailbox.name)
                mailbox_obj.unlink(cr, uid, ids)
                
    def fetch_mail(self, cr, uid, ids, context):
        pass
    
webmail_mailbox()

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

class webmail_email(osv.osv):
    _name="webmail.email"
    _description="User Email"
    _columns={
        'user_id': fields.many2one('res.users', 'User'),
        'account_id': fields.many2one('webmail.server', 'Server'),
        'folder_id': fields.many2one('webmail.mailbox', 'Folder'),
        'message_id': fields.char('Message Id',size=256),
        'active': fields.boolean('Active'),
        'from_user': fields.char('From', size=256),
        'to': fields.char('To', size=256),
        'subject': fields.char('Subject', size=256),
        'date': fields.datetime('Date'),
        'cc': fields.char('Cc', size=256),
        'bcc': fields.char('Bcc', size=256),
        'body': fields.text('Body'),        
        'tag_id': fields.many2one('webmail.tags', 'Tags'),
    }
    _default={
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def default_get(self, cr, uid, fields, context={}):
        data = super(webmail_email,self).default_get(cr, uid, fields, context)
        if context.has_key('mailid') and context.has_key('action'):
            id = context.get('mailid',False)
            action = context.get('action',False)
            if id and action:
                mail = self.browse(cr, uid, id)
                if action=='reply':
                    data['to']=mail.from_user
                elif action=='replyall':
                    data['to']=mail.from_user
                    if mail.cc:
                        data['cc']=mail.cc
                    if mail.bcc:
                        data['bcc']=mail.bcc
        return data
     
    def send_mail(self, cr, uid, ids, context):
        pass
    
webmail_email()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

