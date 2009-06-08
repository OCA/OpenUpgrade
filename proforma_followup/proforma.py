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

from osv import fields, osv
import mx.DateTime
import time
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import threading
import tools
import netsvc

class proforma_followup_step(osv.osv):
    _name = 'proforma.followup_step'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'proforma_line': fields.one2many('proforma.followup.line', 'followup_id', 'Proforma Follow-Up Line'),
        'state' : fields.selection([('draft','Draft'),('running','Running'),('done','Done'),('cancel','Cancel')],'Status'),
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
    _defaults = {
                'state' : lambda * a:'draft'
                 }
    
    def _callback(self, cr, uid, model, func, args):
        args = (args or []) and eval(args)
        m=self.pool.get(model)
        if m and hasattr(m, func):
            f = getattr(m, func)
            f(cr, uid, *args)
            
            
    def send_mail(self,  cr, uid, followup, invoice):
        to = invoice.address_invoice_id.email or None
        if to:
            src = tools.config.options['smtp_user']
            to = [to]
            body = followup.email_body
            data_user = self.pool.get('res.users').browse(cr,uid,uid)
            vals ={
                   'partner_name' : invoice.partner_id.name,
                   'user_signature': data_user.name,
                   'followup_amount': invoice.amount_total ,
                   'date': time.strftime('%Y-%m-%d') ,
                   'company_name': data_user.company_id.name ,
                   'company_currency': data_user.company_id.currency_id.name,
                   }
            
            body = body%vals
            tools.email_send(src,to,followup.subject,body)
        return
    
    def action_run(self, cr, uid, id, context={}):
        self.write(cr, uid, id, {'state' : 'running'})
        return True
        
    def action_cancel(self, cr, uid, id, context={}):
        self.write(cr, uid, id, {'state' : 'cancel'})
        return True
    
    def action_draft(self, cr, uid, id, context={}):
        self.write(cr, uid, id, {'state' : 'draft'})
        return True
      
        
    def action_done(self, cr, uid, id, context={}):
        pro_fol_line = self.pool.get('proforma.followup.line')
        invoice_obj = self.pool.get('account.invoice')
        cr.execute("select l.id from proforma_followup_line l left join proforma_followup_step s on (l.followup_id=s.id)  where s.state='running'")
        line_ids = map(lambda x: x[0],cr.fetchall())
        cr.execute("select id from account_invoice where state='proforma2' and date_invoice is not null")
        invoice_ids = map(lambda x: x[0],cr.fetchall())
        for line in pro_fol_line.browse(cr, uid,line_ids):
            now = mx.DateTime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
            next_days = RelativeDateTime(days= line.days)
            for inv in invoice_obj.browse(cr,uid,invoice_ids):
                if inv.date_invoice:
                    due_date = mx.DateTime.strptime(inv.date_invoice, '%Y-%m-%d') + next_days
                    if now >= due_date:
                        if line.send_email:
                            mail_thread = threading.Thread( target=self.send_mail , args=( cr, uid, line,inv,))
                            mail_thread.run()
                        if line.call_function:
                            self._callback( cr, uid, line.model, line.function, line.args)
                        if line.cancel_invoice:
                            wf_service = netsvc.LocalService('workflow')
                            wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
                else:
                    pass
        self.write(cr, uid, id, {'state' : 'done'})
        return True
                    
proforma_followup_step()

class proforma_followup_line(osv.osv):
    _name = 'proforma.followup.line'
    _description = 'PRO-Forma Followup Criteria'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'sequence': fields.integer('Sequence'),
        'subject': fields.char('Subject', size=64),
        'email_body': fields.text('E-mail Body' , translate=True),
        'days': fields.integer('Days of delay'),
        'followup_id': fields.many2one('proforma.followup_step', 'Proforma step', required=True, ondelete="cascade"),
        'send_email': fields.boolean('Send E-mail?'),
        'call_function': fields.boolean('Call function?'),
        'cancel_invoice': fields.boolean('Cancel Invoice?'),
        'model': fields.char('Object', size=64),
        'function': fields.char('Function', size=64),
        'args': fields.text('Arguments'),
    }
    

proforma_followup_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
