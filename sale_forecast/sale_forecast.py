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

from osv import fields,osv

import time
import mx.DateTime

class sale_forecast(osv.osv):
    _name = "sale.forecast"
    _description = "Sales Forecast"
    _columns = {
        'name': fields.char('Sales Forecast', size=32, required=True),
        'user_id': fields.many2one('res.users', 'Responsible', required=True, select=1),
        'date_from':fields.date('Start Period', required=True),
        'date_to':fields.date('End Period', required=True),
        'line_ids': fields.one2many('sale.forecast.line', 'forecast_id', 'Forecast lines'),
        'state': fields.selection([('draft','Draft'),('open','Open'),('close','Closed'),('cancel','Canceled')], 'State', required=True, select=1),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'draft',
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: (mx.DateTime.now()+mx.DateTime.RelativeDateTime(months=1,day=1,days=-1)).strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,c: uid
    }
    _order = 'date_from desc'
sale_forecast()

class sale_forecast_line(osv.osv):
    _name = "sale.forecast.line"
    _description = "Forecast Line"
    _rec_name = 'user_id'
    
    def _final_evolution(self, cr, uid, ids, name, args, context={}):
        forecast_line =  self.browse(cr, uid, ids)
        result ={forecast_line[0].id :0}
        for line in forecast_line:
            state_dict = {
                'draft' : line.state_draft,
                'confirmed' : line.state_confirmed,
                'done' : line.state_done,
                'cancel' : line.state_cancel
            }
            state = filter(lambda x : state_dict[x],state_dict)
            where = []
            if state :
                where.append(('state','in',state))
            where.append(('user_id','=',line.user_id.id))           
            if line.computation_type in ('invoice_fix','amount_invoiced') :
                obj = 'account.invoice'
                where.append(('date_invoice','>=',line.forecast_id.date_from))
                where.append(('date_invoice','<=',line.forecast_id.date_to))
            elif line.computation_type == 'cases' :
                obj = 'crm.case'
                where.append(('create_date','>=',line.forecast_id.date_from))
                where.append(('date_closed','<=',line.forecast_id.date_to))             
                if line.crm_case_section:
                    section_id = map(lambda x : x.id ,line.crm_case_section)
                    where.append(('section_id','in',section_id))
                if line.crm_case_categ:
                    categ_id = map(lambda x : x.id ,line.crm_case_categ)
                    where.append(('categ_id','in',categ_id))
            else :
                obj = 'sale.order'
                where.append(('date_order','>=',line.forecast_id.date_from))
                where.append(('date_order','<=',line.forecast_id.date_to))          
            searched_ids = self.pool.get(obj).search(cr,uid,where)
            if  line.computation_type  in ('amount_sales','amount_invoiced') :
                res = self.pool.get(obj).browse(cr,uid,searched_ids)
                amount =0
                for r in res:
                    amount += r.amount_untaxed
                print amount
                result[line.id]=amount
            else:   
                result[line.id]=len(searched_ids)       
        return result
    
    _columns = {
        'forecast_id': fields.many2one('sale.forecast', 'Forecast',ondelete='cascade',required =True),
        'user_id': fields.many2one('res.users', 'Salesman',required=True),
        'computation_type' : fields.selection([('invoice_fix','Number of Invoice'),('amount_invoiced','Amount Invoiced'),('cases','No of Cases'),('number_of_sale_order','Number of sale order'),('amount_sales','Amount Sales')],'Computation Base On',required=True),
        'state_draft' : fields.boolean('Draft'),
        'state_confirmed': fields.boolean('Confirmed'),
        'state_done': fields.boolean('Done'),
        'state_cancel': fields.boolean('Cancel'),
        'crm_case_section' : fields.many2many('crm.case.section', 'crm_case_section_forecast', 'forecast_id','section_id', 'Case Section'),
        'crm_case_categ' : fields.many2many('crm.case.categ', 'crm_case_categ_forecast', 'forecast_id','categ_id', 'Case Category',),
        'note':fields.text('Note', size=64),        
        'amount': fields.float('Value Forecasted'),
        'computed_amount': fields.function(_final_evolution, string='Real Value',method=True, store=True,),
        'final_evolution' : fields.selection([('bad','Bad'),('to_be_improved','To Be Improved'),('normal','Noraml'),('good','Good'),('very_good','Very Good')],'Performance',),
        'feedback' : fields.text('Feedback Comment')    
    }
    _order = 'user_id'
    _defaults = {
        'computation_type' : lambda *a : 'invoice_fix'
    }
    
sale_forecast_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

