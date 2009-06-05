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
import pooler

class profile_game_phase_one(osv.osv):
    _name="profile.game.phase1"
    _rec_name = 'state'
    _columns = {
        'step1': fields.boolean('Create Quotation', readonly=True),
        'step1_so_id': fields.many2one('sale.order', 'Quotation / Sale Order', readonly=True),
        'step2': fields.boolean('Print Customer Quotation', readonly=True),
        'step3': fields.boolean('Confirm Sale Order', readonly=True),

        'step4': fields.boolean('Print Request for Quotation', readonly=True),
        'step5': fields.boolean('Change Supplier Price', readonly=True),
        'step6': fields.boolean('Confirm Request for Quotation', readonly=True),

        'step7': fields.boolean('Receive Products from Supplier', readonly=True),
        'step8': fields.boolean('Deliver Products to Customer', readonly=True),

        'step9': fields.boolean('Confirm Draft Invoice', readonly=True),
        'step10': fields.boolean('Print Customer Invoice', readonly=True),

        'state' :fields.selection([
            ('not running','Not Running'),
            ('quotation','Create Quotation'),
            ('print_quote','Print Quotation'),
            ('sale','Confirm Sale Order'),
            ('print_rfq','Print Request for Quotation'),
            ('modify_price','Modify Price RfQ'),
            ('confirm_po','Confirm Purchase Order'),
            ('receive','Receive Products'),
            ('deliver','Deliver Products'),
            ('invoice_create','Confirm Invoice'),
            ('invoice_print','Print Invoice'),
            ('started_phase2','Started Phase Two'),
            ('done','Done'),
        ], 'State', required=True,readonly=True)
    }
    _defaults = {
        'state': lambda *args: 'not running'
    }
    #
    # TODO: check pre process very carefully
    #
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False):
        res = super(profile_game_phase_one, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar)
        p_obj = self.pool.get('profile.game.phase2')
        p_id = p_obj.search(cr,uid,[])
        p_br = p_obj.browse(cr,uid,p_id)
        for rec in p_br:
            if rec.sales_user_id.name or False:
                hr_name = " "
                if rec.hr_user_id:
                   hr_name = rec.hr_user_id.name
                res['arch'] = res['arch'].replace('(SM)', rec.sales_user_id.name)
                res['arch'] = res['arch'].replace('(HRM)',hr_name)
                res['arch'] = res['arch'].replace('(FM)',rec.finance_user_id.name)
                res['arch'] = res['arch'].replace('(LM)', rec.logistic_user_id.name)
                return res
        res['arch'] = res['arch'].replace('(SM)',"")
        res['arch'] = res['arch'].replace('(HRM)',"")
        res['arch'] = res['arch'].replace('(FM)',"")
        res['arch'] = res['arch'].replace('(LM)',"")
        return res

    def error(self, cr, uid,step_id, msg=''):
        err_msg=''
        step=step_id and self.pool.get('game.scenario.step').browse(cr,uid,step_id) or False
        if step:
           err_msg=step.error
        raise Exception("%s -- %s\n\n%s"%('warning', _('Warning !'), err_msg+'\n\n'+msg))

    def pre_process_quotation(self, cr,uid,step_id, object, method,type, *args):
        if (not method) and type!='execute':
            return False
        if ((object not in ("sale.order", 'sale.order.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        return (object in ("sale.order", 'sale.order.line')) and (method in ('create'))

    def post_process_quotation(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid and res:
            return self.write(cr,uid,pid,{'step1':True,'state':'print_quote','step1_so_id':res})
        return False

    def pre_process_print_quote(self,cr,uid,step_id,object, method,type,*args):
        if (type=='execute') and (object not in ("sale.order", 'sale.order.line')) and (method in ('create','write','unlink')):
            self.error(cr, uid, step_id)
        if type=='execute_wkf':
            self.error(cr, uid, step_id)
        return (type=='report') and (object=="sale.order")

    def post_process_print_quote(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step2':True,'state':'sale'})
        return False

    def pre_process_sale(self,cr,uid,step_id,object, method,type,*args):
        if (type=='execute') and (method in ('create','unlink')):
            self.error(cr, uid, step_id)
        if (type=='execute') and (object not in ("sale.order",'sale.order.line')) and (method=='write'):
            self.error(cr, uid, step_id)
        if type!='execute_wkf':
            return False
        if method<>'order_confirm':
            self.error(cr, uid, step_id)
        return True

    def post_process_sale(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step3':True,'state':'print_rfq'})
        return False

    def pre_process_print_rfq(self, cr,uid,step_id, object, method,type, *args):
        if type == 'wizard':
            return False
        if (type=='execute') and ((object not in ("purchase.order", 'purchase.order.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        if type not in ('execute','report'):
            self.error(cr, uid,step_id)
        #if type!='report' and (object in ("purchase.order", 'purchase.order.line') and (method not in ('fields_view_get','create','write','read','button_dummy'))):
        #    self.error(cr, uid,step_id)
        return (type=='report' and (object in ("purchase.quotation")))

    def post_process_print_rfq(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            self.write(cr,uid,pid,{'step4':True,'state':'modify_price'})
            return True
        return False

    def pre_process_modify_price(self,cr,uid,step_id,object, method,type,*args):
        if type=='execute_wkf' and object in ("purchase.order", 'purchase.order.line'):
            self.error(cr, uid,step_id)
        if ((object not in ("purchase.order", 'purchase.order.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        return (object in ('purchase.order.line')) and (method in ('write'))

    def post_process_modify_price(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step5':True,'state':'confirm_po'})
        return False
    def pre_process_confirm_po(self,cr,uid,step_id,object, method,type,*args):
        if type!='execute_wkf':
            return False
        if ((object not in ("purchase.order",'purchase.order.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        return (object in ("purchase.order")) and (method in ('purchase_confirm'))

    def post_process_confirm_po(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step6':True,'state':'receive'})
        return False

    def pre_process_receive(self,cr,uid,step_id,object, method,type,*args):
         # TO DO : fetch name of wizard
        if type!='wizard':
            return False
        wizard_id=args[0]
        object=args[1].get('model',False)
        if object:
            if object not in ("stock.picking"):
                self.error(cr, uid,step_id)
            return object in ("stock.picking") and wizard_id

    def post_process_receive(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step7':True,'state':'deliver'})
        return False
    def pre_process_deliver(self,cr,uid,step_id,object, method,type,*args):
        # TO DO : fetch name of wizard
        if type!='wizard':
            return False

        wizard_id=args[0]
        object=args[1]['model']
        if object not in ("stock.picking"):
            self.error(cr, uid,step_id)
        return object in ("stock.picking") and wizard_id

    def post_process_deliver(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step8':True,'state':'invoice_create'})
        return False

    def pre_process_invoice_create(self,cr,uid,step_id,object, method,type,*args):
        if (type=='execute') and ((object not in ("account.invoice",'account.invoice.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        if (type!='execute_wkf'):
            return False
        if (type=='execute_wkf') and (method<>'invoice_open'):
            self.error(cr, uid,step_id)
        return True

    def post_process_invoice_create(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step9':True,'state':'invoice_print'})
        return False

    def pre_process_invoice_print(self, cr,uid,step_id, object, method,type, *args):
        if type!='report' and (object not in ("account.invoice", 'account.invoice.line')):
            return False
        #if type!='report' and (object in ("account.invoice", 'account.invoice.line') and (method not in ('create','write','read','button_dummy'))):
        #    self.error(cr, uid,step_id)
        return (type=='report' and (object in ("account.invoice", 'account.invoice.line')))

    def post_process_invoice_print(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'retail_phase1')
            sid = self.pool.get('ir.model.data').browse(cr, uid, sid).res_id
            self.pool.get('game.scenario').write(cr, uid, [sid], {'state':'done'})
            return self.write(cr,uid,pid,{'step10':True,'state':'done'})
        return False

    def generate_account_chart(self, cr, uid, ids, context={}):
         company_id = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.id
         chart = self.pool.get('account.chart.template').search(cr, uid, [])
         wiz_id = self.pool.get('wizard.multi.charts.accounts').create(cr, uid, {'company_id':company_id,
                                                                        'chart_template_id':chart[0],'code_digits':6})
         self.pool.get('wizard.multi.charts.accounts').action_create(cr, uid, [wiz_id], context)
         acc_obj = self.pool.get('account.account')
         inc_acc_id = acc_obj.search(cr, uid, [('code','ilike','701000')])[0]
         exp_acc_id = acc_obj.search(cr, uid, [('code','ilike','601000')])[0]
         opening_acc = acc_obj.search(cr, uid, [('code','ilike','890000')])[0]
      #   acc_obj.write(cr ,uid, close_acc, {'type':'other'})

         acc_journal = self.pool.get('account.journal')
         journal_ids = acc_journal.search(cr, uid, [])
         for journal in acc_journal.browse(cr, uid, journal_ids):
            if journal.code in ('JB','SAJ','EXJ','JO'):
                 if journal.code == 'JB':
                     code = '512100'
                 if journal.code == 'SAJ':
                     code = '411100'
                 if journal.code == 'EXJ':
                    code = '401100'
                 if journal.code == 'JO':
                     code = '890000'
                     op_journal = journal
                 account = acc_obj.search(cr, uid, [('code','ilike',code)])[0]
                 acc_journal.write(cr, uid, journal.id, {'default_debit_account_id':account,
                                                                 'default_credit_account_id':account})
#create Opening Balance for the First Fiscal Year.
         period = self.pool.get('account.period').search(cr, uid, [])[0]
         period_obj = self.pool.get('account.period').browse(cr,uid,period)

         for bal in [{'debit':50000,'credit':0.0},{'debit':0.0,'credit':50000.0}]:
             self.pool.get('account.move.line').create(cr, uid, {
                        'debit': bal['debit'],
                        'credit':bal['credit'],
                        'name': 'Opening Balance Entries',
                        'date': period_obj.date_start,
                        'journal_id': op_journal.id,
                        'period_id': period,
                        'account_id': opening_acc,
                    }, {'journal_id': op_journal.id, 'period_id':period})
         for product in self.pool.get('product.product').search(cr, uid, []):
             self.pool.get('product.product').write(cr, uid, product,
                          {'property_account_income':inc_acc_id,'property_account_expense':exp_acc_id})
         return True

    def confirm(self, cr, uid, ids, context={}):
        phase2_obj = self.pool.get('profile.game.phase2')
        phase2_obj.create_fiscalyear_and_period(cr, uid, ids, context)
        self.generate_account_chart(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'quotation'})
        sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'retail_phase1')
        sid = self.pool.get('ir.model.data').browse(cr, uid, sid, context=context).res_id
        self.pool.get('game.scenario').write(cr, uid, [sid], {'state':'running'})
        sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_business_game', 'step_quotation')
        sid = self.pool.get('ir.model.data').browse(cr, uid, sid, context=context).res_id
        return self.pool.get('game.scenario.step').write(cr, uid, [sid], {'state':'running'})

    def check_state(self, cr, uid, context = {}):
        curr_id = self.search(cr, uid, [])[0]
        obj = self.browse(cr, uid, curr_id)
        if obj.state != 'started_phase2':
            return False
        return True

profile_game_phase_one()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {}
    _defaults = {
        'order_policy': lambda *a: 'postpaid',
        }
sale_order()


