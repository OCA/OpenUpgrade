from osv import fields,osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _has_supplier_direct_delivery(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            cr.execute('select id from sale_order_line where is_supplier_direct_delivery=true and order_id=%d' % id)
            results = cr.fetchone()
            if results and len(results) > 0:
                res[id] = True
            else:
                res[id] = False

        return res
    
    _columns = {
        'has_supplier_direct_delivery': fields.function(_has_supplier_direct_delivery, method=True, type='boolean', string="Has Supplier Direct Delivery"),
#        'composite_global_state': fields.function(_composite_global_state, method=True, type='char', size=64, string="Composite Global State"),#TODO
    }

    
    def action_wait(self, cr, uid, ids, context={}):
        print "action_wait"
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                context.update( {'qty_uos': order_line.product_uom_qty})
                if order_line.is_supplier_direct_delivery: #forced manually
                    self.pool.get('sale.order.line').write(cr, uid, order_line.id, {'type': 'make_to_order', 'is_supplier_direct_delivery': True})

        super(sale_order, self).action_wait(cr, uid, ids, context)
        
        
        
    def action_ship_create(self, cr, uid, ids, *args):
        super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        
        for so in self.browse(cr, uid, ids):#TODO ensure that works!!! Why only one po_id is returned from super method?
            for so_line in so.order_line:
                if so_line.is_supplier_direct_delivery:
                    if not (so_line.procurement_id and so_line.procurement_id.related_direct_delivery_purchase_order):
                        continue #Direct delivery impossible for that product; product might have its procurement options not properly configured
                    po = so_line.procurement_id.related_direct_delivery_purchase_order
                    if len(po.order_line) != 1:
                        logger.notifyChannel('DIRECT DELIVERY', netsvc.LOG_ERROR, "Error purchase order with id %d doesn't have a single line" % po.id)
                    else:
                        self.pool.get('purchase.order.line').write(cr, uid, po.order_line[0].id, {'partner_address_id': so.partner_shipping_id.id, 'is_supplier_direct_delivery': True, 'sale_order_line':so_line.id})
                        self.pool.get('sale.order.line').write(cr, uid, so_line.id, {'purchase_order_line': po.order_line[0].id})

        return True


sale_order()



class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def _purchase_order(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for so_line in self.browse(cr, uid, ids):
            res[so_line.id] = so_line.purchase_order_line and so_line.purchase_order_line.order_id.id or False
        return res
    
    def _purchase_order_state(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for so_line in self.browse(cr, uid, ids):
            res[so_line.id] = so_line.purchase_order_line and so_line.purchase_order_line.order_id.state or False
        return res
    
    def _is_supplier_direct_delivery_advised(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for so_line in self.browse(cr, uid, ids):
            context = context.update({'qty': so_line.product_uos_qty}) #TODO check if context is taen into account or do like product_id_change
            res[so_line.id] = so_line.product_id and so_line.product_id.is_direct_delivery_from_product or False
        return res
            
    
    _columns = {
        'is_supplier_direct_delivery': fields.boolean('Is Direct Delivery?'),
        'is_supplier_direct_delivery_advised': fields.function(_is_supplier_direct_delivery_advised, method=True, type='boolean', string="Is Supplier Direct Delivery Advised?"),
        'purchase_order_line':fields.many2one('purchase.order.line', 'Associated Purchase Order Line', required=False),
        'purchase_order':fields.function(_purchase_order, method = True, type = 'many2one', relation = 'purchase.order', string="Related Purchase Order"),
        'purchase_order_state': fields.function(_purchase_order_state, method=True, type='char', size=64, string="Purchase Order State"),
#        'picking_state': fields.function(_picking_state, method=True, type='char', size=64, string="Picking State"), #TODO ensure it works even in two steps delivery
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging)
        
        if product:
            context = {'lang': lang, 'partner_id': partner_id, 'qty': qty}
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            if product_obj.is_direct_delivery_from_product:
                result['value'].update({'type': 'make_to_order', 'is_supplier_direct_delivery': True})
        return result
        
    
    #TODO implement is_supplier_direct_delivery_change to enable canceling the direct delivery manually
    
sale_order_line()