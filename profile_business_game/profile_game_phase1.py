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

class profile_game_config_wizard(osv.osv_memory):
    _name='profile.game.config.wizard'
    _columns = {
        'state':fields.selection([('3','3'),('4','4')],'Number of Players',required=True),
        'finance_name':fields.char('Name of Financial Manager',size='64', required=True),
        'finance_email':fields.char('Email of Financial Manager',size='64'),
        'hr_name':fields.char('Name of Human Resource Manager',size='64', readonly=True,required=False,states={'4':[('readonly',False),('required',True)]}),
        'hr_email':fields.char('Email of Human Resource Manager',size='64',readonly=True,required=False,states={'4':[('readonly',False),('required',False)]}),
        'logistic_name':fields.char('Name of Logistic Manager',size='64', required=True),
        'logistic_email':fields.char('Email of Logistic Manager',size='64'),
        'sale_name':fields.char('Name of Sales Manager',size='64', required=True),
        'sale_email':fields.char('Email of Sales Manager',size='64'),
        'objectives':fields.selection([
            ('on_max_turnover','Maximise Turnover of Last Year'),
            ('on_max_cumulative','Maximise Cumulative Benefit'),
            ('on_max_products_sold','Maximise Number of Products Sold')],'Objectives',required=True),
        'years':fields.selection([
            ('3','3 Years (40 minutes)'),
            ('5','5 Years (1 hour)'),
            ('7','7 Years (1 hours and 20 minutes)')],'Number of Turns',required=True),
        'difficulty':fields.selection([
            ('easy','Easy'),
            ('medium','Medium'),
            ('hard','Hard')],'Difficulty',required=True),
    }
    _defaults = {
        'difficulty': lambda *args: 'medium',
        'years': lambda *args: '5',
        'objectives': lambda *args: 'on_max_turnover',
        'state': lambda *args: '3',
    }


    def action_run(self, cr, uid, ids, context = None):
        game_obj = self.pool.get('profile.game.phase2')
        fiscal_obj = self.pool.get('account.fiscalyear')
        user_obj = self.pool.get('res.users')
        emp_obj = self.pool.get('hr.employee')
        for res in self.read(cr, uid, ids, context = context):
            if res.get('id',False):
                del res['id']
            game_vals = {
                'state':res['state'],
                'objectives':res['objectives'],
                'years':res['years'],
                'difficulty':res['difficulty'],
            }
            players = int(res['state'])
            game_id = game_obj.create(cr,uid,game_vals,context=context)
            for user_name in ['finance','sale','logistic','hr']:
                if user_name == 'hr' and players < 4:
                    continue
                user_ids = user_obj.name_search(cr, uid, user_name)
                user_id = len(user_ids) and user_ids[0][0] or False
                if user_name == 'finance':
                    game_vals['finance_user_id'] = user_id
                if user_name == 'sale':
                    game_vals['sales_user_id'] = user_id
                if user_name == 'logistic':
                    game_vals['logistic_user_id'] = user_id
                if user_name == 'hr':
                    game_vals['hr_user_id'] = user_id
                game_obj.write(cr, uid, game_id, game_vals)
                name = res.get(user_name+'_name','')
                if name:
                    email = res.get(user_name+'_email','')
                    emp_ids = emp_obj.search(cr,uid,[('user_id','=',user_id)])
                    if not len(emp_ids):
                        emp_obj.create(cr,uid,{
                                'name':name.strip(),
                                'work_email':email
                        })
                    else:
                        emp_obj.write(cr,uid,emp_ids,{
                                'name':name.strip(),
                                'work_email':email
                        })
                    user_obj.write(cr,uid,[user_id],{'name':name.strip()})

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj._get_id(cr, uid, 'profile_business_game', 'phase1')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']

        value = {
            'name': 'Business Game',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'profile.game.phase1',
            'view_id': False,
            'res_id' : id,
            'type': 'ir.actions.act_window'
        }
        return value

profile_game_config_wizard()

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
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False, submenu=False):
        res = super(profile_game_phase_one, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
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
        print "object, method,type,*args",object, method,type,args
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
      #  print "object, method,type, *args",object, method,type, args
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
         acc_obj = self.pool.get('account.account')
         acc_journal = self.pool.get('account.journal')
         company_id = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.id

         cr.execute("select id from account_chart_template ")
         chart = map(lambda x: x[0], cr.fetchall())

         wiz_id = self.pool.get('wizard.multi.charts.accounts').create(cr, uid, {'company_id':company_id,
                                                                        'chart_template_id':chart[0],'code_digits':6})
         self.pool.get('wizard.multi.charts.accounts').action_create(cr, uid, [wiz_id], context)

         cr.execute("select id from account_account where code in ('601000','701000','890000')")
         accounts = cr.fetchall()

         cr.execute('select id from account_journal')
         journal_ids = map(lambda x: x[0], cr.fetchall())

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
                        'account_id': accounts[2][0],
                    }, {'journal_id': op_journal.id, 'period_id':period})
         for product in self.pool.get('product.product').search(cr, uid, []):
             self.pool.get('product.product').write(cr, uid, product,
                          {'property_account_income':accounts[1][0],'property_account_expense':accounts[0][0]})
         return True

    def assign_limited_menus(self,cr,uid,ids,context={}):
        user_obj = self.pool.get('res.users')
        menus = ['Sales Management','Sales Orders','New Quotation','Purchase Management','Purchase Orders','Request For Quotations','Stock Management','Incoming Products','Outgoing Products','Financial Management','Invoices','Customer Invoices','Draft Customer Invoices']
        menu_obj = self.pool.get('ir.ui.menu')

        sale_menu_ids = menu_obj.search(cr,uid,['|','|',('name','like','Sales Management'),('name','like','New Quotation'),('name','like','Sales Orders')])
        hr_menu_ids = menu_obj.search(cr,uid,['|','|',('name','like','Request For Quotations'),('name','like','Purchase Management'),('name','like','Purchase Orders')])
        log_menu_ids = menu_obj.search(cr,uid,['|','|',('name','like','Incoming Products'),('name','like','Outgoing Products'),('name','like','Stock Management')])
        fin_menu_ids = menu_obj.search(cr,uid,['|','|','|',('name','like','Draft Customer Invoices'),('name','like','Financial Management'),('name','like','Invoices'),('name','like','Customer Invoices')])

        gp = self.pool.get('res.groups')
        admin_gp = gp.search(cr,uid,[('name','like','Administrator / Access Rights')])
        all_menus = menu_obj.search(cr,uid,[])

        user_name = ['sale','logistic','hr','finance']
        user_ids = user_obj.search(cr, uid, [('login','in',user_name)])
        for user in user_obj.browse(cr, uid, user_ids):
            for group in user.groups_id:
                gp.write(cr,uid,group.id,{'menu_access':[[6,0,[]]]})
                if group.name == 'Finance / Invoice':
                    gp.write(cr,uid,group.id,{'menu_access':[[6,0,fin_menu_ids]]})
                if group.name in ('Purchase / User','HR / Invoice'):
                    gp.write(cr,uid,group.id,{'menu_access':[[6,0,hr_menu_ids]]})
                if group.name == 'Stock / Worker' :
                    gp.write(cr,uid,group.id,{'menu_access':[[6,0,log_menu_ids]]})
                if group.name == 'Sale / Salesman':
                    gp.write(cr,uid,group.id,{'menu_access':[[6,0,sale_menu_ids]]})
        for menu in menu_obj.browse(cr,uid,all_menus):
            if not menu.name in menus:
                menu_obj.write(cr,uid,menu.id,{'groups_id':[[6,0,admin_gp]]})
        return

    def confirm(self, cr, uid, ids, context={}):
        phase2_obj = self.pool.get('profile.game.phase2')
        model_obj = self.pool.get('ir.model.data')
        phase2_obj.create_fiscalyear_and_period(cr, uid, ids, context)
        self.generate_account_chart(cr, uid, ids, context)
        self.assign_limited_menus(cr,uid,ids,context)
        self.write(cr, uid, ids, {'state':'quotation'})
        sid = model_obj._get_id(cr, uid, 'profile_business_game', 'retail_phase1')
        sid = model_obj.browse(cr, uid, sid, context=context).res_id
        self.pool.get('game.scenario').write(cr, uid, [sid], {'state':'running'})
        sid = model_obj._get_id(cr, uid, 'profile_business_game', 'step_quotation')
        sid = model_obj.browse(cr, uid, sid, context=context).res_id
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


