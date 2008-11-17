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

class mrp_repair(osv.osv):
    _name = 'mrp.repair'
    _description = 'Repairs Order'
    
    def _invoiced(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for repair in self.browse(cursor, user, ids, context):
            res[repair.id] = True
            if not repair.invoice_id:
                res[repair.id] = False
            if repair.invoice_id.state <> 'paid':
                res[repair.id] = False

        return res
    
    _columns = {
        'name' : fields.char('Name',size=24),
        'product_id': fields.many2one('product.product', string='Product to Repair', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'partner_id' : fields.many2one('res.partner', 'Partner', select=True),
        'address_id': fields.many2one('res.partner.address', 'Delivery Address', domain="[('partner_id','=',partner_id)]"),
        'prodlot_id': fields.many2one('stock.production.lot', 'Lot Number', select=True, domain="[('product_id','=',product_id)]"),
        'state': fields.selection([
            ('draft','Quotation'),
            ('confirmed','Confirmed'),
            ('2binvoiced','To be Invoiced'),
            ('shipping_except','Shipping Exception'),
            ('invoice_except','Invoice Exception'),
            ('done','Done'),
            ('cancel','Cancel')
            ], 'State', readonly=True, help="Gives the state of the Repairs Order"),
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
         'invoiced': fields.function(_invoiced, method=True, string='Paid', type='boolean'),
        'shipped' : fields.boolean('Picked', readonly=True),
    }
    
    _defaults = {
        'state': lambda *a: 'draft',
        'invoice_method': lambda *a: 'none',
        'pricelist_id': lambda self, cr, uid,context : self.pool.get('product.pricelist').search(cr,uid,[('type','=','sale')])[0]
    }
    
    
    def onchange_product_id(self, cr, uid, ids, prod_id=False, move_id=False ):
        if not prod_id:
            return  {'value':{'prodlot_id': False , 'move_id': False, 'location_id' :  False}}
        if move_id:
            move =  self.pool.get('stock.move').browse(cr, uid, move_id)
            product = self.pool.get('product.product').browse(cr, uid, [prod_id])[0]
            date = move.date_planned#time.strftime('%Y-%m-%d')
            limit = mx.DateTime.strptime(date, '%Y-%m-%d %H:%M:%S') + RelativeDateTime(months=product.warranty, days=-1)
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

    
    def onchange_lot_id(self, cr, uid, ids, lot ):
        if not lot:
            return {'value':{'location_id': False , 'move_id' :  False}}
        lot_info = self.pool.get('stock.production.lot').browse(cr, uid, [lot])[0]
        move_id = self.pool.get('stock.move').search(cr, uid,[('prodlot_id','=',lot)] )
        if move_id: 
            move = self.pool.get('stock.move').browse(cr, uid, move_id )[0]
#            self.onchange_product_id(cr, uid, ids, prod_id, move_id)
            return {'value':{'location_id': move.location_dest_id.id ,  'move_id': move.id }}
        else:
            return {'value':{'location_id': False , 'move_id' :  False}}
        
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

    def action_wait(self, cr, uid, ids, *args):
        for o in self.browse(cr, uid, ids):
            if (o.invoice_method == 'none'):
                self.write(cr, uid, [o.id], {'state': 'confirmed'})
            elif (o.invoice_method == 'b4repair'):
                self.write(cr, uid, [o.id], {'state': '2binvoiced'})
            elif (o.invoice_method == 'after_repair'):
                self.write(cr, uid, [o.id], {'state': 'confirmed'})
            
            mrp_line_obj = self.pool.get('mrp.repair.lines')
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
        for order in self.browse(cr, uid, ids, context={}):
            if order.invoice_id:
                self.pool.get('account.invoice').write(cr, uid, [order.invoice_id.id], {'state':'cancel'})
            
            if not (order.partner_id.id and order.partner_invoice_id.id):
                return False
            if (order.invoice_method != 'none'):
                a = order.partner_id.property_account_receivable.id
                inv = {
                    'name': 'Repair: '+order.product_id.name,
                    'type': 'out_invoice',
                    'reference': "Repair%dP%d"%(order.id,order.product_id.id),
                    'account_id': a,
                    'partner_id': order.partner_id.id,
                    'address_invoice_id': order.address_id.id,
                    'currency_id' : order.pricelist_id.currency_id.id,
                    'comment': order.internal_notes,
                }
                inv_obj = self.pool.get('account.invoice')
                inv_id = inv_obj.create(cr, uid, inv)
                self.write(cr, uid, order.id , {'invoice_id' : inv_id})
                if order.operations:
                    for operation in order.operations:
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
                if order.fees_lines:
                    for fee in order.fees_lines:
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
                self.write(cr, uid, [order.id], {'state' : 'confirmed'})
                return inv_id
            else:
                return False
    

    def action_invoice_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'invoice_except', 'invoice_id':False})
        return True
    
    def action_ship_create(self, cr, uid, ids, *args):
        picking_id=False
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for repair in self.browse(cr, uid, ids, context={}):
            if repair.location_dest_id:
                output_id = repair.location_dest_id.id
                for line in repair.operations:
                    proc_id=False
                    date_planned = time.strftime('%Y-%m-%d %H:%M:%S')
                    pr_id = self.pool.get('product.product').browse(cr, uid, line.product_id.id)
                    if line.product_id and pr_id.product_tmpl_id.type in ('product', 'consu'):
                        location_id = line.location_id.id
                        if not picking_id:
                            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                'origin': repair.product_id.code, # + (repair.partner_id and  repair.partner_id.name) or ' ',
                                'type': 'out',
                                'state': 'auto',
                                'move_type': 'one',
                                'address_id': repair.address_id.id,
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
                            'product_uos_qty': line.product_uos_qty,
                            'product_uos': (line.product_uos and line.product_uos.id)\
                                    or line.product_uom.id,
                            'product_packaging' : line.product_packaging.id,
                            'address_id': repair.address_id.id,
                            'location_id': location_id,
                            'location_dest_id': output_id,
                            'tracking_id': False,
                            'state': 'draft',
                            'note': line.notes,
                        }
                        move_id = self.pool.get('stock.move').create(cr, uid, vals)
                        proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                            'name': repair.name or 'Repair',
                            'origin': repair.name,
                            'date_planned': date_planned,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'location_id': repair.location_id.id,
                            'procure_method': 'make_to_stock' ,# NEEDS TO BE CHANGED
                            'move_id': line.id,
                        })
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                        self.pool.get('mrp.repair.lines').write(cr, uid, [line.id], {'procurement_id': proc_id})
                    elif line.product_id and pr_id.product_tmpl_id.type=='service':
                        proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                            'name': line.name or 'Repair',
                            'origin': repair.name,
                            'date_planned': date_planned,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'location_id': repair.location_id.id,
                            'procure_method': 'make_to_stock' ,# NEEDS TO BE CHANGED
                        })
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                        self.pool.get('mrp.repair.lines').write(cr, uid, [line.id], {'procurement_id': proc_id})
                    else:
                        #
                        # No procurement because no product in the sale.order.line.
                        #
                        pass
    
                val = {}
                if picking_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                self.write(cr, uid, [repair.id], val)
                
        return True

    def procurement_lines_get(self, cr, uid, ids, *args):
        res = []
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.operations:
                if line.procurement_id:
                    res.append(line.procurement_id.id)
        return res
    
    def test_state(self, cr, uid, ids, mode, *args):
        assert mode in ('finished', 'canceled'), _("invalid mode for test_state")
        finished = True
        canceled = False
        write_done_ids = []
        write_cancel_ids = []
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.operations:
                if line.procurement_id and (line.procurement_id.state != 'done') and (line.state!='done'):
                    finished = False
                if line.procurement_id and line.procurement_id.state == 'cancel':
                    canceled = True
                # if a line is finished (ie its procuremnt is done or it has not procuremernt and it
                # is not already marked as done, mark it as being so...
                if ((not line.procurement_id) or line.procurement_id.state == 'done') and line.state != 'done':
                    write_done_ids.append(line.id)
                # ... same for canceled lines
                if line.procurement_id and line.procurement_id.state == 'cancel' and line.state != 'cancel':
                    write_cancel_ids.append(line.id)
        if write_done_ids:
            self.pool.get('mrp.repair.lines').write(cr, uid, write_done_ids, {'state': 'done'})
        if write_cancel_ids:
            self.pool.get('mrp.repair.lines').write(cr, uid, write_cancel_ids, {'state': 'cancel'})

        if mode=='finished':
            return finished
        elif mode=='canceled':
            return canceled
        
    def action_ship_end(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids,{'shipped' : 1})
        for order in self.browse(cr, uid, ids):
            val = {}
            if (order.invoice_method=='after_repair'):
                val['state'] = '2binvoiced'
            else:
                val['state'] = 'confirmed'
            self.write(cr, uid, [order.id], val)
        return True
mrp_repair()


class mrp_repair_lines(osv.osv):
    _name = 'mrp.repair.lines'
    _description = 'Repair Operations'
     
    def _get_price(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for val in self.browse(cr, uid, ids):
            res[val.id] = {}
            if val.repair_id:
                current_date = time.strftime('%Y-%m-%d')
                if current_date < val.repair_id.guarantee_limit:
                    res[val.id]['price_unit'] = 0.0
                    res[val.id]['invoice'] = False
                if current_date >= val.repair_id.guarantee_limit:
                    price = 0.0
                    pricelist = val.repair_id.pricelist_id.id
                    if pricelist:
                        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], val.product_id.id , 1.0, val.repair_id.partner_id.id)[pricelist]
                    if price is False:
                         warning={
                            'title':'No valid pricelist line found !',
                            'message':
                                "Couldn't find a pricelist line matching this product and quantity.\n"
                                "You have to change either the product, the quantity or the pricelist."
                            }
                    else:
                        res[val.id]['price_unit'] = price
                        res[val.id]['invoice'] = True
        return res
    
    def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        return res
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
            cur = line.repair_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    _columns = {
                'name' : fields.char('Name',size=24),
                'repair_id': fields.many2one('mrp.repair', 'Repair Order Ref',ondelete='cascade', select=True),
                'type': fields.selection([('add','Add'),('remove','Remove')],'Type'),
#                'invoice': fields.boolean('Invoice', readonly=True),
                'invoice': fields.function(_get_price,  method=True, store= True, type='boolean', string='Invoice', multi='invoice'),
                'delay': fields.float('Delivery Delay', required=True),
                'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)],  required=True),
                'invoiced': fields.boolean('Invoiced'),
                'procurement_id': fields.many2one('mrp.procurement', 'Procurement'),
                'price_unit': fields.function(_get_price,  method=True, store= True, type='float', string='Price', multi='price_unit'),
                'price_net': fields.function(_amount_line_net, method=True, string='Net Price'),
                'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
                'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes'),
                'property_ids': fields.many2many('mrp.property', 'sale_order_line_property_rel', 'order_id', 'property_id', 'Properties'),
                'address_allotment_id' : fields.many2one('res.partner.address', 'Allotment Partner'),
                'product_uom_qty': fields.float('Quantity (UoM)', digits=(16,2), required=True),
                'product_uom': fields.many2one('product.uom', 'Product UoM', required=True),
                'product_uos_qty': fields.float('Quantity (UOS)'),
                'product_uos': fields.many2one('product.uom', 'Product UOS'),
                'product_packaging': fields.many2one('product.packaging', 'Packaging'),
                'move_ids': fields.one2many('stock.move', 'sale_line_id', 'Inventory Moves', readonly=True),
                'discount': fields.float('Discount (%)', digits=(16,2)),
                'notes': fields.text('Notes'),
                'th_weight' : fields.float('Weight'),
                'location_id': fields.many2one('stock.location', 'Source Location', required=True, select=True),
                'location_dest_id': fields.many2one('stock.location', 'Dest. Location', required=True, select=True),
                'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done'),('cancel','Canceled')], 'Status', required=True, readonly=True),
    }
     
     
    def product_id_change(self, cr, uid, ids, pricelist, product, uom=False, product_uom_qty = 0,partner_id=False ):
        if not product:
            return {'value': {'product_uom_qty' : 0.0, 'product_uom': False},'domain': {'product_uom': []}}
        product_obj =  self.pool.get('product.product').browse(cr, uid, product)
        result = {}
        warning = {}
        if not uom:
            result['product_uom'] = product_obj.uom_id.id
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],}
        
        if not pricelist:
            warning={
                'title':'No Pricelist !',
                'message':
                    'You have to select a pricelist in the Repair form !\n'
                    'Please set one before choosing a product.'
                }
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, product_uom_qty or 1.0, partner_id, {
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
                
        return {'value': result , 'domain' :domain, 'warning':warning}
     
     
    def onchange_operation_type(self, cr, uid, ids, type ):
        if not type:
            return {'value':{'location_id': False , 'location_dest_id' :  False}}
        stock_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Stock')])[0]
        produc_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Default Production')])[0]
        if type == 'add':
            return {'value':{'location_id': stock_id , 'location_dest_id' : produc_id}}
        if type == 'remove':
            return {'value':{'location_id': produc_id}}
        
    _defaults = {
                 'name' : lambda *a: 'Repair Operation',
                 'state': lambda *a: 'draft',
                 }
    
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
    
    def product_id_change(self, cr, uid, ids, product, uom=False):
        if not product:
            return {'value': {'product_uom_qty' : 0.0, 'product_uom': False},'domain': {'product_uom': []}}
        
        product_obj =  self.pool.get('product.product').browse(cr, uid, product)
        result = {}
        if not uom:
            result['product_uom'] = product_obj.uom_id.id
        domain = {'product_uom':
                    [('category_id', '=', product_obj.uom_id.category_id.id)],}
        return {'value': result ,'domain': domain}
    
mrp_repair_fee()


class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
                'state': fields.selection([('draft','Draft'),('waiting','Waiting'),('confirmed','Confirmed'),('assigned','Assigned'),('done','Done'),('cancel','cancel'),('in_repair','In Repair')], 'Status',),# readonly=True, select=True),
                'repair_ids' : fields.one2many('mrp.repair', 'move_id', 'Repairs'),
            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
