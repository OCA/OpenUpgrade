from osv import fields, osv

class mrp_procurement(osv.osv):
    _inherit = "mrp.procurement"
    
    _columns = {
        #Field that is used temporarily: in the sale.action_ship_create method, the procurement is created but isn't yet linked back to the 
        #sale_order_line. So when the procurement itself generate a purchase order, we can't find back the sale order line yet.
        #Instead, we set the procurement.related_direct_delivery_purchase_order once the procurement created the purchase order
        #so later on, back in sale.py, once the procurement is linked back to the sale order line, we can find back the crate purchase order, sigh! 
        'related_direct_delivery_purchase_order': fields.many2one('purchase.order', 'Related Direct Delivery Purchase Order'),
    }

    def action_po_assign(self, cr, uid, ids, context={}):
        po_id = super(mrp_procurement, self).action_po_assign(cr, uid, ids, context)
        customer_location_id = self.pool.get('purchase.order').browse(cr, uid, po_id).partner_id.property_stock_customer.id
        self.pool.get('purchase.order').write(cr, uid, po_id, {'location_id':  customer_location_id})
        
        for procurement in self.browse(cr, uid, ids):#TODO ensure that works!!! Why only one po_id is returned from super method?
            self.pool.get('mrp.procurement').write(cr, uid, procurement.id, {'related_direct_delivery_purchase_order': po_id})

mrp_procurement()