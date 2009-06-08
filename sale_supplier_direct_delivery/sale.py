from osv import fields,osv


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def _is_supplier_direct_delivery_advised(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for so_line in self.browse(cr, uid, ids):
            if so_line.product_id:
                product_id = so_line.product_id.id #we do that to pass the qty in context properly; we can't use the order_line directly since product_id_change doesn't have a sale.order line reference
                if context == None:
                    context = {}
                
                context.update({'qty': so_line.product_uos_qty})
                product_obj = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                res[so_line.id] = product_obj.is_direct_delivery_from_product
            else:
                res[so_line.id] = False
        return res
            
    
    _columns = {
        'is_supplier_direct_delivery': fields.boolean('Is Direct Delivery?'),
        'is_supplier_direct_delivery_advised': fields.function(_is_supplier_direct_delivery_advised, method=True, type='boolean', string="Is Supplier Direct Delivery Advised?"),
        'purchase_order_line':fields.many2one('purchase.order.line', 'Related Purchase Order Line', required=False),
        'purchase_order': fields.related('purchase_order_line', 'order_id', type='many2one', relation='purchase.order', string='Related Purchase Order'),
        'purchase_order_state': fields.related('purchase_order', 'state', type='char', size=64, string='Purchase Order State'),
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False):
        #TODO added flag arg -> toss Tiny!!!

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position)
        
        if product:
            context = {'lang': lang, 'partner_id': partner_id, 'qty': qty}
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            if product_obj.is_direct_delivery_from_product:
                result['value'].update({'type': 'make_to_order', 'is_supplier_direct_delivery': True})
        return result
    
sale_order_line()


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
        'has_supplier_direct_delivery': fields.function(_has_supplier_direct_delivery, method=True, type='boolean', string="Has Supplier Direct Delivery", store=True, select=1),#        'composite_global_state': fields.function(_composite_global_state, method=True, type='char', size=64, string="Composite Global State"),#TODO
    }

    
    def action_wait(self, cr, uid, ids, context={}):
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                context.update( {'qty_uos': order_line.product_uom_qty})
                if order_line.is_supplier_direct_delivery: #forced manually
                    self.pool.get('sale.order.line').write(cr, uid, order_line.id, {'type': 'make_to_order', 'is_supplier_direct_delivery': True})

        super(sale_order, self).action_wait(cr, uid, ids, context)
        
        
    #cross linking direct delivery sale orders and purchase orders
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
                    
                    #we remove the associated moves from Stock -> Customers as it will be replaced by moves Suppliers -> Customers
                    #see purchase_order.action_picking_create for more details
                    for move in so_line.move_ids:
                        move_id = move.id
                        picking_id = move.picking_id.id
                        # delete the move
                        self.pool.get('stock.move').action_cancel(cr, uid, [move_id])
                        self.pool.get('stock.move').write(cr, uid, move_id, {'state': 'draft'})
                        self.pool.get('stock.move').unlink(cr, uid, [move_id])
                        # check if picking is empty. if yes, delete the picking
                        move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',picking_id)] )
                        if not move_ids:
                            self.pool.get('stock.picking').action_cancel(cr, uid, [picking_id])
                            self.pool.get('stock.picking').unlink(cr, uid, [picking_id])

        return True


sale_order()