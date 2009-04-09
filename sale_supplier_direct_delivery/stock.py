from osv import fields,osv

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    _columns = {
        'is_supplier_direct_delivery': fields.boolean('Is Direct Delivery?'),
    }
    
stock_picking()