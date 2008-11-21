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

import time
from osv import fields,osv
import netsvc
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
from tools import config
class mrp_repair(osv.osv):
    _name = 'mrp.repair'
    _description = 'Repairs Order'   
    
    
    _columns = {
        'name' : fields.char('Name',size=24, required=True),
        'product_id': fields.many2one('product.product', string='Product to Repair', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'partner_id' : fields.many2one('res.partner', 'Partner', select=True),
        'address_id': fields.many2one('res.partner.address', 'Delivery Address', domain="[('partner_id','=',partner_id)]"),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lot Number', select=True, domain="[('product_id','=',product_id)]"),
        'state': fields.selection([
            ('draft','Quotation'),
            ('confirmed','Confirmed'),
            ('ready','Ready to Repair'),
            ('under_repair','Under Repair'),
            ('2binvoiced','To be Invoiced'),            
            ('invoice_except','Invoice Exception'),
            ('done','Done'),
            ('cancel','Cancel')
            ], 'Repair State', readonly=True, help="Gives the state of the Repair Order"),
        'location_id': fields.many2one('stock.location', 'Current Location', required=True, select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'location_dest_id': fields.many2one('stock.location', 'Delivery Location', readonly=True, states={'draft':[('readonly',False)]}),
        'move_id': fields.many2one('stock.move', 'Move',required=True, domain="[('product_id','=',product_id)]", readonly=True, states={'draft':[('readonly',False)]}),#,('location_dest_id','=',location_id),('prodlot_id','=',prodlot_id)
        'guarantee_limit': fields.date('Guarantee limit'),
        'operations' : fields.one2many('mrp.repair.lines', 'repair_id', 'Operation Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
        'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice to',  domain="[('partner_id','=',partner_id)]"),
        'invoice_method':fields.selection([
            ("none","No Invoice"),
            ("b4repair","Before Repair"),
            ("after_repair","After Repair")
           ], "Invoice Method", 
            select=True, states={'draft':[('readonly',False)]}, readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'fees_lines' : fields.one2many('mrp.repair.fee', 'repair_id', 'Fees Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'internal_notes' : fields.text('Internal Notes'),
        'quotation_notes' : fields.text('Quotation Notes'),
        'invoiced': fields.boolean('Invoiced', readonly=True),
        'repaired' : fields.boolean('Repaired', readonly=True),
    }
    
    _defaults = {
        'state': lambda *a: 'draft',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'mrp.repair'),
        'invoice_method': lambda *a: 'none',
        'pricelist_id': lambda self, cr, uid,context : self.pool.get('product.pricelist').search(cr,uid,[('type','=','sale')])[0]
    }
    
    def copy(self, cr, uid, id, default=None,context={}):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'shipped':False,
            'invoiced':False,
            'invoice_id': False,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'mrp.repair'),
        })
        return super(mrp_repair, self).copy(cr, uid, id, default, context)


    def onchange_product_id(self, cr, uid, ids, prod_id=False, move_id=False ):
        if not prod_id:
            return  {'value':{'prodlot_id': False , 'move_id': False,'guarantee_limit':False, 'location_id' :  False}}
        if move_id:
            move =  self.pool.get('stock.move').browse(cr, uid, move_id)
            product = self.pool.get('product.product').browse(cr, uid, prod_id)
            date = move.date_planned
            limit = mx.DateTime.strptime(date, '%Y-%m-%d %H:%M:%S') + RelativeDateTime(months=product.warranty)
            result = {
                'guarantee_limit': limit.strftime('%Y-%m-%d'),
            }
            return { 'value' : result }
        return {}
    
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'address_id': False ,'partner_invoice_id' : False , 'pricelist_id' : self.pool.get('product.pricelist').search(cr,uid,[('type','=','sale')])[0]}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part],  ['delivery','invoice','default'])
        partner = self.pool.get('res.partner').browse(cr, uid,part)
        pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
        return {'value':{'address_id': addr['delivery'], 'partner_invoice_id' :  addr['invoice'] ,  'pricelist_id': pricelist}}

    
    def onchange_lot_id(self, cr, uid, ids, lot,product_id ):
        if not lot:
            return {'value':{'location_id': False , 'move_id' :  False}}
        lot_info = self.pool.get('stock.production.lot').browse(cr, uid, [lot])[0]
        move_id = self.pool.get('stock.move').search(cr, uid,[('prodlot_id','=',lot)] )
        if move_id: 
            move = self.pool.get('stock.move').browse(cr, uid, move_id )[0]
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            date = move.date_planned
            limit = mx.DateTime.strptime(date, '%Y-%m-%d %H:%M:%S') + RelativeDateTime(months=product.warranty)            
            return {'value':{'location_id': move.location_dest_id.id ,  'move_id': move.id,'guarantee_limit': limit.strftime('%Y-%m-%d') }}
        else:
            return {'value':{'location_id': False , 'move_id' :  False,'guarantee_limit':False}}
        
    def action_cancel_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        mrp_line_obj = self.pool.get('mrp.repair.lines')
        for repair in self.browse(cr, uid, ids):
            mrp_line_obj.write(cr, uid, [l.id for l in repair.operations], {'state': 'draft'})
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_create(uid, 'mrp.repair', id, cr)
        return True

    def action_confirm(self, cr, uid, ids, *args):        
        mrp_line_obj = self.pool.get('mrp.repair.lines')
        for o in self.browse(cr, uid, ids):
            if (o.invoice_method == 'b4repair'):                
                self.write(cr, uid, [o.id], {'state': '2binvoiced'})
            else:
                self.write(cr, uid, [o.id], {'state': 'confirmed'})   
                mrp_line_obj.write(cr, uid, [l.id for l in o.operations], {'state': 'confirmed'})
        return True
    
    def action_cancel(self, cr, uid, ids, context={}):
        ok=True
        mrp_line_obj = self.pool.get('mrp.repair.lines')
        for repair in self.browse(cr, uid, ids):
            mrp_line_obj.write(cr, uid, [l.id for l in repair.operations], {'state': 'cancel'})
        self.write(cr,uid,ids,{'state':'cancel'})
        return True
    
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['2binvoiced','done']):
        inv_id=False        
        for repair in self.browse(cr, uid, ids, context={}):
            if repair.invoice_id:                                
                continue           
            if not (repair.partner_id.id and repair.partner_invoice_id.id):
                raise osv.except_osv('No partner !','You have to select a partner in the repair form ! ')
            if (repair.invoice_method != 'none'):
                a = repair.partner_id.property_account_receivable.id
                inv = {
                    'name': repair.name +':'+repair.product_id.name,
                    'origin':repair.name +':'+repair.product_id.name,
                    'type': 'out_invoice',                    
                    'account_id': a,
                    'partner_id': repair.partner_id.id,
                    'address_invoice_id': repair.address_id.id,
                    'currency_id' : repair.pricelist_id.currency_id.id,
                    'comment': repair.internal_notes,
                }
                inv_obj = self.pool.get('account.invoice')
                inv_id = inv_obj.create(cr, uid, inv)
                self.write(cr, uid, repair.id , {'invoiced':True,'invoice_id' : inv_id}) 
                                
                for operation in repair.operations:
                    if operation.to_invoice == True:
                        invoice_line_id=self.pool.get('account.invoice.line').create(cr, uid, {
                            'invoice_id' : inv_id, 
                            'name' : operation.product_id.name,
                            'account_id' : a,
                            'quantity' : operation.product_uom_qty,
                            'uos_id' : operation.product_uom.id,
                            'price_unit' : operation.price_unit,
                            'price_subtotal' : operation.product_uom_qty*operation.price_unit,
                            'product_id' : operation.product_id.id
                            })                   
                        self.pool.get('mrp.repair.lines').write(cr, uid, [operation.id], {'invoiced':'True','invoice_line_id':invoice_line_id})
                for fee in repair.fees_lines:
                    invoice_fee_id=self.pool.get('account.invoice.line').create(cr, uid, {
                        'invoice_id' : inv_id,
                        'name' : fee.product_id.name,
                        'account_id' : a,
                        'quantity' : fee.product_uom_qty,
                        'uos_id' : fee.product_uom.id,
                        'product_id' : fee.product_id.id,
                        'price_unit' : fee.price_unit,
                        'price_subtotal' : fee.product_uom_qty*fee.price_unit
                        })
                
        self.action_invoice_end(cr, uid, ids)
        return inv_id
    

    def action_invoice_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'invoice_except'})
        return True

    def action_repair_ready(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'ready'})
        return True

    def action_repair_start(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'under_repair'})
        return True
    
    def action_invoice_end(self, cr, uid, ids, context={}):        
        for order in self.browse(cr, uid, ids):
            val = {}             
            if (order.invoice_method=='b4repair'):
                val['state'] = 'ready'
            else:                
                #val['state'] = 'done'                 
                pass
            self.write(cr, uid, [order.id], val)
        return True     

    def action_repair_end(self, cr, uid, ids, context={}):        
        for order in self.browse(cr, uid, ids):
            val = {}
            val['repaired']=True
            if (not order.invoiced and order.invoice_method=='after_repair'):
                val['state'] = '2binvoiced'  
            elif (not order.invoiced and order.invoice_method=='b4repair'):
                val['state'] = 'ready'
            else:                
                #val['state'] = 'done'                 
                pass
            self.write(cr, uid, [order.id], val)
        return True     

    def action_repair_done(self, cr, uid, ids, *args):        
        picking_id=False        
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for repair in self.browse(cr, uid, ids, context={}):
            if repair.location_dest_id:                
                location_dest_id = False
                for line in repair.operations:
                    proc_id=False
                    date_planned = time.strftime('%Y-%m-%d %H:%M:%S')
                    pr_id = self.pool.get('product.product').browse(cr, uid, line.product_id.id)
                    if line.product_id and pr_id.product_tmpl_id.type in ('product', 'consu'):
                        location_id = False
                        stock_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Stock')])[0]
                        produc_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Default Production')])[0]
                        if line.type == 'add':
                            location_id= stock_id 
                            location_dest_id= produc_id
                        if line.type == 'remove':
                            location_id=produc_id
                        if not picking_id:
                            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                'origin': repair.name,
                                'type': 'out',
                                'state': 'auto',
                                'move_type': 'one',
                                'address_id': repair.address_id and repair.address_id.id or False,
                                'note': repair.internal_notes,
                                'invoice_state': 'none',
                            })
                        
                        vals = {
                            'name': line.product_id.name[:64],
                            'picking_id': picking_id,
                            'product_id': line.product_id.id,
                            'date_planned': date_planned,
                            'product_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'product_uos_qty': line.product_uom_qty,
                            'product_uos': line.product_uom.id,                            
                            'address_id': repair.address_id and repair.address_id.id or False,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,
                            'tracking_id': False,
                            'state': 'draft',                            
                        }
                        move_id = self.pool.get('stock.move').create(cr, uid, vals)                      
                
    				
                if picking_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            self.write(cr, uid, [repair.id], {'state':'done'})
            self.pool.get('mrp.repair.lines').write(cr, uid, map(lambda x:x.id,repair.operations), {'state':'done'})    
        return True   
        
           
mrp_repair()


class mrp_repair_lines(osv.osv):
    _name = 'mrp.repair.lines'
    _description = 'Repair Operations Lines'    
    

    def _amount_line(self, cr, uid, ids, field_name, arg, context):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_uom_qty
            cur = line.repair_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    _columns = {
                'name' : fields.char('Name',size=64,required=True),
                'repair_id': fields.many2one('mrp.repair', 'Repair Order Ref',ondelete='cascade', select=True),
                'type': fields.selection([('add','Add'),('remove','Remove')],'Type'),
                'to_invoice': fields.boolean('To Invoice'),                
                'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)],  required=True),
                'invoiced': fields.boolean('Invoiced'),                
                'price_unit': fields.float('Unit Price', required=True, digits=(16, int(config['price_accuracy']))),
                'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal',digits=(16, int(config['price_accuracy']))),                
                'product_uom_qty': fields.float('Quantity (UoM)', digits=(16,2), required=True),
                'product_uom': fields.many2one('product.uom', 'Product UoM', required=True),          
                'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line', readonly=True),            
                'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done'),('cancel','Canceled')], 'Status', required=True, readonly=True),
    }
    _defaults = {                 
                 'state': lambda *a: 'draft',
                 'product_uom_qty':lambda *a:1,                 
    }
     
     
    def product_id_change(self, cr, uid, ids, pricelist, product, uom=False, product_uom_qty = 0,partner_id=False ):
        if not product:
            return {'value': {'product_uom_qty' : 0.0, 'product_uom': False},'domain': {'product_uom': []}}
        product_obj =  self.pool.get('product.product').browse(cr, uid, product)
        result = {}
        domain = {}
        warning = {}       
        result['name'] = product_obj.partner_ref
        result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
        if not pricelist:
            warning={
                'title':'No Pricelist !',
                'message':
                    'You have to select a pricelist in the Repair form !\n'
                    'Please set one before choosing a product.'
                }
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, product_uom_qty, partner_id, {
                        'uom': uom,
                        })[pricelist]
            
            if price is False:
                 warning={
                    'title':'No valid pricelist line found !',
                    'message':
                        "Couldn't find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist."
                    }
            else:
                result.update({'price_unit': price, 'price_subtotal' :price*product_uom_qty })
        return {'value': result , 'warning':warning}
     
     
    def onchange_operation_type(self, cr, uid, ids, type ):
        if not type:
            return {'value':{'location_id': False , 'location_dest_id' :  False}}
        stock_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Stock')])[0]
        produc_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Default Production')])[0]
        if type == 'add':
            return {'value':{'location_id': stock_id , 'location_dest_id' : produc_id}}
        if type == 'remove':
            return {'value':{'location_id': produc_id}}
        
    
    
mrp_repair_lines()

class mrp_repair_fee(osv.osv):
    _name = 'mrp.repair.fee'
    _description = 'Repair Fees line'
    _columns = {
        'repair_id': fields.many2one('mrp.repair', 'Repair Order Ref', required=True, ondelete='cascade', select=True),
        'name': fields.char('Description', size=8, select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_uom_qty': fields.float('Quantity', digits=(16,2), required=True),
        'price_unit': fields.float('Unit Price', required=True),
        'product_uom': fields.many2one('product.uom', 'Product UoM', required=True),
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, uom=False, product_uom_qty = 0,partner_id=False ):
        if not product:
            return {'value': {'product_uom_qty' : 0.0, 'product_uom': False},'domain': {'product_uom': []}}
        
        product_obj =  self.pool.get('product.product').browse(cr, uid, product)
        result = {}
        if not pricelist:
            warning={
                'title':'No Pricelist !',
                'message':
                    'You have to select a pricelist in the Repair form !\n'
                    'Please set one before choosing a product.'
                }
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],product, product_uom_qty or 1.0, partner_id, {
                        'uom': uom,
                        })[pricelist]
            if price is False:
                 warning={
                    'title':'No valid pricelist line found !',
                    'message':
                        "Couldn't find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist."
                    }
            else:
                result.update({'price_unit': price})
        if not uom:
            result['product_uom'] = product_obj.uom_id.id        
        return {'value': result}
    
mrp_repair_fee()


#class stock_move(osv.osv):
#    _inherit = "stock.move"
#    _columns = {
#                'state': fields.selection([('draft','Draft'),('waiting','Waiting'),('confirmed','Confirmed'),('assigned','Assigned'),('done','Done'),##('cancel','cancel'),('in_repair','In Repair')], 'Status',),# readonly=True, select=True),
#                'repair_ids' : fields.one2many('mrp.repair', 'move_id', 'Repairs'),
#            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
