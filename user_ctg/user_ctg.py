# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import time
import datetime
import tools
import netsvc
from osv import fields,osv
import os

class ctg_type(osv.osv):
    _name = 'ctg.type'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'code': fields.char('Code', size=64, required=True, select=True),
    }  
ctg_type()

class users(osv.osv):    
    _inherit = "res.users"
    _columns = {        
        'lp_login': fields.char('Launchpad ID', size=64),
        'ctg_line':fields.one2many('ctg.line','rewarded_user_id','CTG Lines', readonly=True)
    }
users()

class ctg_line(osv.osv):
    _name = 'ctg.line'
    _columns = {        
        'ctg_type_id':fields.many2one('ctg.type', 'CTG Type', required=True),
        'rewarded_user_id':fields.many2one('res.users', 'Rewarded User', required=True),
        'points': fields.float('Points', required=True),
        'date_ctg':fields.date('CTG Date', required=True),
    }
    _defaults = {
        'points': lambda *a: 0.0,
        'date_ctg': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _order = 'points desc'  

    def get_LP_points(self, cr, uid, automatic=False, use_new_cursor=False, context=None):                
        from lp_server import LP_Server        
        user_obj = self.pool.get('res.users')
        ctg_type_obj = self.pool.get('ctg.type')
        lpserver = LP_Server()
        lpserver.cachedir = os.path.join(tools.config['root_path'],lpserver.cachedir)
        lpserver.credential_file = os.path.join(tools.config['root_path'],lpserver.credential_file)         
        lp = lpserver.get_lp()       
        user_ids = user_obj.search(cr, uid, [('lp_login','!=',False)])
        users = user_obj.read(cr, uid, user_ids, ['name','lp_login'])
        for user in users:
            user_res = lpserver.get_lp_people_info(lp, user['lp_login']) 
            type_ids = ctg_type_obj.search(cr, uid, [('code','=', 'development')])            
            if len(type_ids):
                ctg_ids = self.search(cr, uid, [('rewarded_user_id','=',user['id']),('ctg_type_id','=',type_ids[0])])
                ctg_res = self.read(cr, uid, ctg_ids, ['points','date_ctg'])                       
                points = 0.0
                for ctg in ctg_res:
                    points += float(ctg['points'])
                points = user_res[user['lp_login']]['karma'] - points
                if points > 0.0:
                    self.create(cr, uid, {'rewarded_user_id':user['id'],'ctg_type_id':type_ids[0],'points':points})    
        return True

    def send_mail(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        # send mail to user regarding them CTG points of month by cron job
        if not context:
            context = {}
        date = context.get('date',False) or datetime.date.today()
        report_ctg_line_obj = self.pool.get('report.ctg.line')
        report_ctg_line_ids = report_ctg_line_obj.search(cr, uid, [('name','=',date.strftime('%Y:%m'))])
        if len(report_ctg_line_ids):
            mail_body = {}
            for report_ctg_line in report_ctg_line_obj.browse(cr, uid, report_ctg_line_ids):
                if report_ctg_line.rewarded_user_id.address_id and report_ctg_line.rewarded_user_id.address_id.email:
                    mail_to = report_ctg_line.rewarded_user_id.address_id.email
                    mail_body[report_ctg_line.rewarded_user_id.id]= [mail_to,report_ctg_line.ctg_type_id.name,report_ctg_line.points] 
            for mail_to, ctg_type,points in mail_body.values():
                body = 'You obtain following CTG points of %s month:\n' %(date.strftime('%Y:%m')) + '%s : %s \n'%(ctg_type, points)
                user = tools.config['email_from']
                if not user:
                    raise osv.except_osv(_('Error'), _("Please specify server option --smtp-from !"))
        
                subject = 'Your CTG points of %s month in OpenERP' %(date.strftime('%Y:%m'))
                logger = netsvc.Logger()
                if tools.email_send(user, [mail_to], subject, body, debug=False, subtype='html') == True:
                    logger.notifyChannel('email', netsvc.LOG_INFO, 'Email successfully send to : %s' % (mail_to))
                else:
                    logger.notifyChannel('email', netsvc.LOG_ERROR, 'Failed to send email to : %s' % (mail_to))      
        return
    
    
ctg_line()

class report_ctg_line(osv.osv):
    _name = "report.ctg.line"
    _description = "CTG points per user per month"
    _auto = False
    _columns = {
        'name' : fields.char('Month',size=64),
        'ctg_type_id': fields.many2one('ctg.type', 'CTG Type'),
        'points': fields.float('Points', required=True),
        'rewarded_user_id':fields.many2one('res.users', 'Rewarded User', required=True),
    }
    _order = 'name desc'

    def init(self, cr):
        cr.execute("""
            create or replace view report_ctg_line as ( 
                select 
                    min(l.id) as id,
                    to_char(l.date_ctg,'YYYY:mm') as name,
                    sum(l.points) as points,                    
                    l.rewarded_user_id,
                    l.ctg_type_id
                from ctg_line l                
                group by
                    to_char(l.date_ctg,'YYYY:mm'), l.rewarded_user_id, l.ctg_type_id
            )""")
report_ctg_line()

class ctg_feedback(osv.osv):
    _name = 'ctg.feedback'
    _columns = {
        'name': fields.char('Title', size=64, required=True, select=True),
        'ctg_line_id':fields.many2one('ctg.line', 'CTG', readonly=True),
        'ctg_type_id':fields.many2one('ctg.type', 'CTG Type', required=True),
        'user_to':fields.many2one('res.users', 'Feedback by User', required=True),
        'responsible':fields.many2one('res.users', 'Responsible User', required=True),
        'points': fields.selection([
            ('0','Not Satisfacted At All'),
            ('3','Not Satisfacted'),
            ('6','Satisfacted'),
            ('10','Very Satisfacted'),            
            ], 'Points'),
        'date_feedback':fields.date('Feedback Date', required=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('open','Open'),
            ('done','Done'),
            ('cancel','Canceled'),            
            ], 'State', required=True),
        'note': fields.text('Body'),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'date_feedback': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _order = 'name desc'  

    def action_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'cancel'})
        
    def action_open(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'open'})
        # TODO : Send mail to user regarding link of feedback page, saying that they have to fill a feedback and give url to it

    def action_done(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'done'})
        # TODO : create CTG Line with ctg_type ?
        # points : for customer satisfaction type , need to calaculate avg. points base on projects ?
                    # example : customer give 2 points for 1 project / 3 projects ?
    def action_cancel_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'draft'})

    def check_feedback(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        # draft to open feedback . It is called by cron job
        draft_feedback_ids = self.search(cr, uid, [('date_feedback','<=',time.strftime('%Y-%m-%d')),('state','=','draft')])
        if len(draft_feedback_ids):
            self.action_open(cr, uid, draft_feedback_ids, context=context)
        # open to cancel feedback if it is not done since long time (1 month)
        current_date = datetime.date.today()
        year = current_date.year
        if current_date.month == 1:
            year = current_date.year - 1
            month = 12
        else:
            month = current_date.month - 1
        d = datetime.date(year, month, current_date.day)
        open_feedback_ids = self.search(cr, uid, [('date_feedback','<=',d.strftime('%Y-%m-%d')),('state','=','open')])  
        if len(open_feedback_ids):
            self.action_cancel(cr, uid, open_feedback_ids, context=context)

ctg_feedback()



class document_file(osv.osv):
    _inherit = 'ir.attachment' 
    
    def read(self, cr, user, ids, fields_to_read=None, context=None, load='_classic_read'):
        result = super(document_file,self).read(cr, user, ids, fields_to_read, context=context, load=load)
        current_date = datetime.date.today()
        feedback_date = current_date
        ctg_type_obj = self.pool.get('ctg.type')
        ctg_type_ids = ctg_type_obj.search(cr,user,[('code','=','dms')])
        if len(ctg_type_ids) and context.get('download',False):
            ctg_feedback_obj = self.pool.get('ctg.feedback')
            for res in result:
                cr.execute('select name,title,user_id from ir_attachment where id = %s' %(res['id']))
                document = cr.dictfetchone()
                ctg_feedback_id = ctg_feedback_obj.create(cr, user, {
                        'name' : 'Feedback of Document : %s' %(document['title']),                        
                        'ctg_type_id': ctg_type_ids[0],
                        'user_to':user,
                        'responsible':document['user_id'],        
                        'date_feedback': feedback_date.strftime('%y-%m-%d')}, context)
        return result

document_file()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    #Hint : What to Do ? If Remove the Invoice.
    
    def action_move_create(self, cr, uid, ids, *args): 
        result = super(account_invoice,self).action_move_create(cr, uid, ids, args)
        ctg_line_obj = self.pool.get('ctg.line')
        ctg_type_obj = self.pool.get('ctg.type')
        ctg_type_ids = ctg_type_obj.search(cr,uid,[('code','=','sales')])
        new_date = datetime.date.today() + datetime.timedelta(days=2)
        for invoice in self.browse(cr,uid,ids):
            if len(ctg_type_ids):
                ctg_line_obj.create(cr, uid,{
                        'ctg_type_id':ctg_type_ids[0],
                        'rewarded_user_id':uid,
                        'date_ctg': new_date,
                        'points':invoice.amount_untaxed})
        return result
    
    def action_cancel(self, cr, uid, ids, *args):
        ctg_type_obj = self.pool.get('ctg.type')
        ctg_line_obj = self.pool.get('ctg.line')
        invoices = self.browse(cr,uid,ids)            
        ctg_type_ids = ctg_type_obj.search(cr,uid,[('code','=','sales')])
        for invoice in invoices:
            if invoice.state == 'open':
                if len(ctg_type_ids):
                    ctg_line_obj.create(cr, uid, {
                                'ctg_type_id': ctg_type_ids[0],
                                'rewarded_user_id' : uid,
                                'points':-invoice.amount_untaxed
                                })      
        result = super(account_invoice,self).action_cancel(cr, uid, ids, args)             
        return result 
    
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def create(self, cr, uid, vals, context={}):
        result = super(account_invoice_line,self).create(cr, uid, vals, context) 
        if vals.has_key('account_analytic_id') and vals['account_analytic_id']:            
            project_obj = self.pool.get('project.project')      
            feedback_obj = self.pool.get('ctg.feedback')
            project_ids = project_obj.search(cr, uid, [('category_id','=',vals['account_analytic_id'])])
            projects = project_obj.browse(cr, uid, project_ids)
            ctg_type_ids = self.pool.get('ctg.type').search(cr,uid,[('code','=','customer satisfaction')])
            new_date = datetime.date.today() + datetime.timedelta(days=2)
            if len(ctg_type_ids):
                for project in projects:
                        feedback_obj.create(cr, uid, {
                                    'name':'Feedback of %s Project' %(project.name),
                                    'ctg_type_id':ctg_type_ids[0],
                                    'user_to':uid,
                                    'responsible':project.manager.id,
                                    'date_feedback':new_date,
                        })
        return result

account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
