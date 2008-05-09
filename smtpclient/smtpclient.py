# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv
import pooler
import binascii
import base64
import os
import time
import smtplib
import mimetypes
from optparse import OptionParser
from email import Encoders
from email.Message import Message
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate

import netsvc
import random
import hashlib



class SmtpClient(osv.osv):
    _name = 'email.smtpclient'
    _description = 'Email Client'
    _columns = {
        'name' : fields.char('Server Name', size=256, required=True),
        'from' : fields.char('Email From', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'email' : fields.char('Email Address', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'user' : fields.char('User Name', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'password' : fields.char('Password', size=256, required=True, invisible=True, readonly=True, states={'new':[('readonly',False)]}),
        'server' : fields.char('SMTP Server', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'port' : fields.char('SMTP Port', size=256, required=True, readonly=True, states={'new':[('readonly',False)]}),
        'ssl' : fields.boolean("Use SSL?", readonly=True, states={'new':[('readonly',False)]}),
        'users_id': fields.many2many('res.users', 'res_smtpserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'state': fields.selection([
            ('new','Not Verified'),
            ('waiting','Waiting for Verification'),
            ('confirm','Verified'),
        ],'Server Status', select=True, readonly=True),
        'active' : fields.boolean("Active"),
        'date_create': fields.date('Date Create', required=True, readonly=True, states={'new':[('readonly',False)]}),
        'test_email' : fields.text('Test Message'),
        'verify_email' : fields.text('Verify Message', readonly=True, states={'new':[('readonly',False)]}),
        'code' : fields.char('Verification Code', size=256),
        'type' : fields.selection([("default", "Default"),("account", "Account"),("sale","Sale"),("stock","Stock")], "Server Type",required=True),
        'history_line': fields.one2many('email.smtpclient.history', 'server_id', 'History')
    }
    
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'new',
    }
    
    def init(self, cr):
        self.server = None
        self.smtpServer = None
        
    def change_email(self, cr, uid, ids, email):
        if email.index('@'):
            user = email[0:email.index('@')]
            return {'value':{'user':user}}
        else:
            return {'value':{'user':email}}
        
    def check_permissions(self, cr, uid, ids):
        cr.execute('select * from res_smtpserver_group_rel where sid=%s and uid=%s' % (ids[0], uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        
        return True
    
    def test_verivy_email(self, cr, uid, ids, toemail, test=False, code=False):
        
        self.open_connection(cr, uid, ids, ids[0])
        
        if test and self.server['state'] != 'confirm':
            pooler.get_pool(cr.dbname).get('email.smtpclient.history').create \
                (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'server_id' : ids[0],'name':'Please Verify Email Server, without verification you can not send Email(s).'})
            raise osv.except_osv('Server Error !', 'Please Verify Email Server, without verification you can not send Email(s).')           
        
        try:
            if test and self.server['state'] == 'confirm':
                body = str(self.server['test_email'])
            else:
                body = str(self.server['verify_email'])
                if code:
                    key = code
                else:
                    key = hashlib.md5(time.strftime('%Y-%m-%d %H:%M:%S') + toemail).hexdigest();
                    
                body = body.replace("%(code)", key)
                
            user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid])[0]
            body = body.replace("%(user)", user.name)
            
            if len(body.strip()) <= 0:
                raise osv.except_osv('Message Error !', 'Please Configure Email Server Messagess [Verification / Test]')
            
            msg = MIMEText(body or '', _charset='utf-8')
            
            if not test and not self.server['state'] == 'confirm':
                msg['Subject'] = 'TinyERP SMTP server Email Registration Code!!!'
            else:
                msg['Subject'] = 'TinyERP Test Email!!!'
            
            msg['To'] = toemail
            msg['From'] = str(self.server['from'])
            self.smtpServer.sendmail(str(self.server['email']), toemail, msg.as_string())
        except Exception, e:
            return False
        
        return True
        
    def open_connection(self, cr, uid, ids, serverid=False, permission=True):
        if serverid:
            self.server = self.read(cr, uid, [serverid])[0]
        else:
            raise osv.except_osv('Read Error !', 'Unable to read Server Settings')
        
        if permission:
            if not self.check_permissions(cr, uid, ids):
                raise osv.except_osv('Permission Error !', 'You have no Permission to Access SMTP Server : %s ' % (self.server['name'],) )
                
        if self.server:
            try:
                self.smtpServer = smtplib.SMTP()
                self.smtpServer.debuglevel = 5
                self.smtpServer.connect(str(self.server['server']),self.server['port'])
                
                if self.server['ssl']:
                    self.smtpServer.ehlo()
                    self.smtpServer.starttls()
                    self.smtpServer.ehlo()
                    
                self.smtpServer.login(str(self.server['user']),str(self.server['password']))
            except Exception, e:
                raise osv.except_osv('SMTP Server Error !', e)
            
        return True
    
    def send_email(self, cr, uid, ids,emailto,subject,resource_id,report_name,file_name,body):

        self.open_connection(cr, uid, ids, ids[0])
        
        def create_report(self,cr,uid,res_ids,report_name,file_name):
            ret_file_name = file_name+'.pdf'
            if not report_name or not res_ids:
                return (False,Exception('Report name and Resources ids are required !!!'))

            try:
                service = netsvc.LocalService("report."+report_name);
                (result,format) = service.create(cr,uid,[res_ids],{},{})
                fp = open(ret_file_name,'wb+');
                fp.write(result);
                fp.close();
            except Exception,e:
                print 'Exception in create report:',e
                return (False,str(e))
        #end try:
        
            return (True,ret_file_name)
    
        file=create_report(self,cr,uid,resource_id,report_name,file_name)[1]
        try:
            if self.server['state'] == 'confirm':
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['To'] = emailto
                msg['From'] = str(self.server['from'])
                msg.attach(MIMEText(body or '', _charset='utf-8'))
                part = MIMEBase('application', "octet-stream")               
                part.set_payload( open(file,"rb").read())
               
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                msg.attach(part)                                        
                self.smtpServer.sendmail(str(self.server['email']), emailto, msg.as_string())
                report_id = pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr, uid, [('report_name','=',report_name)], context=False)
                report_model=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').read(cr,uid,report_id,['model'])[0]['model']
                model_id=pooler.get_pool(cr.dbname).get('ir.model').search(cr, uid, [('model','=',report_model)], context=False)[0]               
                pooler.get_pool(cr.dbname).get('email.smtpclient.history').create \
                (cr, uid, {'date_create':time.strftime('%Y-%m-%d %H:%M:%S'),'server_id' : ids[0],'name':'The Email is sent successfully to corresponding address','email':emailto,'model':model_id,'resource_id':resource_id})
        except Exception, e:
            print 'Exception :',e
            return False     
        
        return True
SmtpClient()

class HistoryLine(osv.osv):
    _name = 'email.smtpclient.history'
    _description = 'Email Client History'
    _columns = {
        'name' : fields.text('Description',required=True),
        'date_create': fields.datetime('Date'),
        'user_id':fields.many2one('res.users', 'Username', readonly=True, select=True),
        'server_id' : fields.many2one('email.smtpclient', 'Smtp Server', ondelete='set null', required=True),
        'model':fields.many2one('ir.model', 'Model', readonly=True, select=True),
        'resource_id':fields.integer('Resource ID', readonly=True),
        'email':fields.char('Email',size=64,readonly=True),
    }
    
    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def create(self, cr, uid, vals, context=None):
        super(HistoryLine,self).create(cr, uid, vals, context)
        cr.commit()
HistoryLine()

class report_smtp_server(osv.osv):
    _name = "report.smtp.server"
    _description = "Server Statestics"
    _auto = False
    _columns = {
        'name': fields.char('Server',size=64,readonly=True),
        'model':fields.char('Model',size=64, readonly=True),
        'history':fields.char('History',size=64,readonly=True),
        'no':fields.integer('# of Activity',readonly=True),
     }
    def init(self, cr):
         cr.execute("""
            create or replace view report_smtp_server as (
                 select min(c.id) as id,count(*) as no,h.name as history,c.name as name from email_smtpclient c,email_smtpclient_history h group by c.name,h.name
                              )
         """)
report_smtp_server()
