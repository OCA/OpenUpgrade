from osv import osv, fields

class portal_training_purchase_line_supplier(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'confirmed_supplier' : fields.boolean('Confirmed by Supplier'),
    }

portal_training_purchase_line_supplier()
