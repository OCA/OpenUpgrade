from osv import osv
from osv import fields

class PurchaseOrder(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    _columns = {
        'name': fields.char('Order Description', size=64, required=True, select=True),
    }
    
    _defaults = {
        'name': lambda *a: 'PO/'
    }

    def wkf_confirm_order(self, cr, uid, ids, context={}):
        number = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order')
        self.write(cr, uid, ids, {'name':number})
        super(PurchaseOrder, self).wkf_confirm_order(cr, uid, ids, context)

PurchaseOrder()
