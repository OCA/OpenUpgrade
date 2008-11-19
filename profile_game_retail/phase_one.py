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

from osv import fields, osv
import pooler

class profile_game_retail_phase_one(osv.osv):
    _name="profile.game.retail.phase1"
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
            ('done','Done'),
        ], 'State', required=True,readonly=True)
    }
    _defaults = {
        'state': lambda *args: 'not running'
    }
    #
    # TODO: check pre process very carefully
    #
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        res = super(profile_game_retail_phase_one, self).fields_view_get(cr, user, view_id, view_type, context, toolbar)

        res['arch'] = res['arch'].replace('role1', 'Fabien')
        res['arch'] = res['arch'].replace('role2', 'Fabien')
        res['arch'] = res['arch'].replace('role3', 'Fabien')
        res['arch'] = res['arch'].replace('role4', 'Fabien')
        return res
    def error(self, cr, uid,step_id, msg=''):
        err_msg=''
        step=step_id and self.pool.get('game.scenario.step').browse(cr,uid,step_id) or False
        if step:
           err_msg=step.error
        raise Exception("%s -- %s\n\n%s"%('warning', 'Warning !', err_msg+'\n\n'+msg))

    def pre_process_quotation(self, cr,uid,step_id, object, method,type, *args):
        if (not method) and type!='execute':
            return False
        if ((object not in ("sale.order", 'sale.order.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        return (object in ("sale.order", 'sale.order.line')) and (method in ('create'))

    def post_process_quotation(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid and res:
            return self.write(cr,uid,pid,{'step1':True,'state':'print_quote','step1_so_id':res})
        return False

    def pre_process_print_quote(self,cr,uid,step_id,object, method,type,*args):
        if type!='report' and (object not in ("sale.order", 'sale.order.line')):
            return False

        if type!='report' and (object in ("sale.order", 'sale.order.line') and (method not in ('read','button_dummy','write'))):
            self.error(cr, uid,step_id)
        return (type=='report' and (object in ("sale.order", 'sale.order.line')))

    def post_process_print_quote(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id

        if pid:
            return self.write(cr,uid,pid,{'step2':True,'state':'sale'})
        return False

    def pre_process_sale(self,cr,uid,step_id,object, method,type,*args):
        print 'PRE Process', object, method, type
        if (type!='execute_wkf'):

            return False
        if ((object not in ("sale.order",'sale.order.line')) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        print 'ok'
        return (object in ("sale.order")) and (method in ('order_confirm'))

    def post_process_sale(self,cr,uid,step_id,object, method,type,*args):
        print 'POST Process', object, method, type
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            #proc_obj = self.pool.get('mrp.procurement')
            #proc_obj.run_scheduler(cr, uid, automatic=True, use_new_cursor=cr.dbname)
            print 'Complex'
            return self.write(cr,uid,pid,{'step3':True,'state':'print_rfq'})
        print 'False'
        return False

    def pre_process_print_rfq(self, cr,uid,step_id, object, method,type, *args):
        print 'Print RFQ', object, step_id, method, type
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
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid and res:
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
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
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
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step6':True,'state':'receive'})
        return False


    def pre_process_receive(self,cr,uid,step_id,object, method,type,*args):
         # TO DO : fetch name of wizard
        if type!='wizard':
            return False
        wizard_id=args[0]
        object=args[1]['model']
        if object not in ("stock.picking"):
            self.error(cr, uid,step_id)
        return object in ("stock.picking") and wizard_id

    def post_process_receive(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
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
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step8':True,'state':'invoice_create'})
        return False

    def pre_process_invoice_create(self,cr,uid,step_id,object, method,type,*args):
        if type!='execute_wkf':
            return False
        if ((object not in ("account.invoice")) and (method in ('create','write','unlink'))):
            self.error(cr, uid,step_id)
        return (object in ("account.invoice")) and (method in ('invoice_open'))

    def post_process_invoice_create(self,cr,uid,step_id,object, method,type,*args):
        res=args[-1]
        res=res and res.get('result',False) or False
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
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
        pid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'phase1')
        pid = self.pool.get('ir.model.data').browse(cr, uid, pid).res_id
        if pid:
            return self.write(cr,uid,pid,{'step10':True,'state':'done'})
        return False



    def confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'quotation'})
        sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'retail_phase1')
        sid = self.pool.get('ir.model.data').browse(cr, uid, sid, context=context).res_id
        self.pool.get('game.scenario').write(cr, uid, [sid], {'state':'running'})
        sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_retail', 'step_quotation')
        sid = self.pool.get('ir.model.data').browse(cr, uid, sid, context=context).res_id
        return self.pool.get('game.scenario.step').write(cr, uid, [sid], {'state':'running'})

profile_game_retail_phase_one()

