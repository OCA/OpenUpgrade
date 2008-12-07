from osv import fields,osv

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _has_supplier_direct_delivery(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            cr.execute('select id from purchase_order_line where is_supplier_direct_delivery=true and order_id=%d' % id)
            results = cr.fetchone()
            if results and len(results) > 0:
                res[id] = True
            else:
                res[id] = False

        return res
    
    _columns = {
        'has_supplier_direct_delivery': fields.function(_has_supplier_direct_delivery, method=True, type='boolean', string="Has Supplier Direct Delivery"),
    }
    
purchase_order()


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    
    def _get_partner_address_id(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = (rec.sale_order_line.order_id.partner_shipping_id.id) or False
        return result
    
    _columns = {
        'partner_address_id': fields.function(_get_partner_address_id, method=True, type='many2one', relation='res.partner.address', string='Address'),
        'sale_order_line':fields.many2one('sale.order.line', 'Address', required=False),
        'is_supplier_direct_delivery': fields.boolean('Is Direct Delivery?'),
    }
    
purchase_order_line()