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
        'lp_login': fields.char('Login', size=64),
        'lp_password': fields.char('Password', size=64),
        'ctg_line':fields.one2many('ctg.line','rewarded_user_id','CTG Lines')
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

    def get_LP_points(self, cr, uid, context={}):
        # TODO : get points from LP and create ctg line. It is called by cron job
        return

    def _send_mail(self, cr, uid, context={}):
        # send mail to user regarding them CTG points of month by cron job
        date = context.get('date',False) or datetime.date.today()
        report_obj = self.pool.get('report.ctg.line')
        report_ids = report_obj.search(cr, uid, [('name','=',d.strftime('%Y:%m'))])
        mail_body = {}
        for report in report_obj.browse(cr, uid, report_ids):
            if report.rewarded_user_id.address_id and report.rewarded_user_id.address_id.email:
                mail_to = report.rewarded_user_id.address_id.email
                if mail_to not in mail_body:
                    mail_body[mail_to] = ''
                mail_body[mail_to][report.ctg_type_id.name] = report.points
    
        for mail_to, value in mail_body.items():
            body = 'You obtain following CTG points of %s month:\n' %(d.strftime('%Y:%m'))
            for ctg_type, points in value:
                body += '%s : %s \n'%(ctg_type, points)
            user = config['email_from']
            if not user:
                raise osv.except_osv(_('Error'), _("Please specify server option --smtp-from !"))
    
            subject = 'Your CTG points of %s month in OpenERP' %(d.strftime('%Y:%m'))
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
                    to_char(l.date_ctg,'YYYY:IW') as name,
                    sum(l.points) as points,                    
                    l.rewarded_user_id,
                    l.ctg_type_id
                from ctg_line l                
                group by
                    to_char(l.date_ctg,'YYYY:IW'), l.rewarded_user_id, l.ctg_type_id
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
            ], 'Points', required=True),
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

    def _check_feedback(self, cr, uid, context={}):
        # draft to open feedback . It is called by cron job
        draft_feedback_ids = self.search(cr, uid, [('date_feedback','<=',time.strftime('%Y-%m-%d')),('state','=','draft')])
        if len(draft_ids):
            self.action_open(cr, uid, draft_feedback_ids, context=context)
        # open to cancel feedback if it is not done since long time (1 month)
        current_date = datetime.date.today()
        if current_date.month == 1:
            current_date.year -= 1
            current_date.month = 12
        else:
            current_date.month += 1
        d = datetime.date(current_date.year, current_date.month, current_date.day)
        open_feedback_ids = self.search(cr, uid, [('date_feedback','<=',d.strftime('%Y-%m-%d')),('state','=','open')])  
        if len(open_feedback_ids):
            self.action_cancel(cr, uid, open_feedback_ids, context=context)

ctg_feedback()



class document_file(osv.osv):
    _inherit = 'ir.attachment' 
    def read(self, cr, user, ids, fields_to_read=None, context=None, load='_classic_read'):
        result = super(document_file,self).read(cr, user, ids, fields_to_read=fields_to_read, context=context, load=load)
        current_date = datetime.date.today()
        feedback_date = current_date
        #ctg_type_id = 
        if context.get('download',False):
            ctg_feedback_obj = self.pool.get('ctg.feedback')
            for res in result:
                r = cr.execute('select name,title,user_id from res_users where id = %s' %(res['id']))
                document = r.fetchone()
                ctg_feedback_obj.create(cr, user, {
                        'name' : 'Feedback of Document : %s' %(document['title']),                        
                        'ctg_type_id': ctg_type_id,
                        'user_to':user,
                        'responsible':document['user_id'],        
                        'date_feedback': feedback_date.strftime('%y-%m-%d')})
        #'state': fields.selection({[]})
            # TODO : create feedback for DMS CTG Type . 
        return result

document_file()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def action_move_create(self, cr, uid, ids, *args):        
        result = super(account_invoice,self).action_move_create(self, cr, uid, ids, args)
        for invoice in self.browse(cr, uid, ids):
            ctg_feedback_obj = self.pool.get('ctg.feedback')
            # TODO : create ctg line for invoice saleman with type = sales , points = total untaxes amount
            
        return result

    def create(self, cr, uid, vals, context={}):
        result = super(account_invoice,self).create(self, cr, uid, vals, context)
        # TODO : feedback should be created with date = invoiced date, with responsible = the user responsible of the analytic account used
        
        return result

account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
