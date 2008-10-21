# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

class profile_game_detail_phase_one(osv.osv):
    _name="profile.game.detail.phase1"
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
        ], 'State', required=True, readonly=True)
    }
    _defaults = {
        'state': lambda *args: 'not running'
    }
    def pre_process_quotation(self, cr,uid, object, method, *args):
        if (object not in ("sale.order", 'sale.order.line')) and (method in ('create','write','unlink')):
            return False

        print 'pre process of quotation', cr, uid, args
        res= args[-1]
        model=res and res.get('model',False) or False
        print model
        if model and model=='sale.order':
             return True
        return False

    def post_process_quotation(cr,uid,*args):
		# TO DO 
        print 'post process of quotation'    
        res=args[-1]
        res=res and res.get('result',False) or False
        print res        
        #self.write(cr,uid,{'step1':True,'step1_so_id':res})
        return True 
    def pre_process_print_quote(cr,uid,ids,*args):
		# TO DO 
        print 'pre process of print quotation'       
        return True 
    def post_process_print_quote(cr,uid,ids,*args):
		# TO DO 
        print 'post process of print quotation'        
        return True
    def pre_process_sale(cr,uid,ids,*args):
		# TO DO 
        print 'pre process of sale'        
        return True
    def post_process_sale(cr,uid,ids,*args):
		# TO DO 
        print 'post process of sale'        
        return True

    def confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'quotation'})
        sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_detail', 'retail_phase1')
        sid = self.pool.get('ir.model.data').browse(cr, uid, sid, context=context).res_id
        print 'Game Detail', sid
        self.pool.get('game.scenario').write(cr, uid, [sid], {'state':'running'})
        sid = self.pool.get('ir.model.data')._get_id(cr, uid, 'profile_game_detail', 'step_quotation')
        sid = self.pool.get('ir.model.data').browse(cr, uid, sid, context=context).res_id
        print 'Game Quotation', sid
        self.pool.get('game.scenario.step').write(cr, uid, [sid], {'state':'running'})

profile_game_detail_phase_one()

