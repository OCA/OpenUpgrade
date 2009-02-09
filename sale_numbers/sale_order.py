from osv import osv
from osv import fields

class SaleOrder(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns = {
        'name': fields.char('Order Description', size=64, required=True, select=True),
    }
    
    _defaults = {
        'name': lambda *a: 'SO/'
    }

    def action_wait(self, cr, uid, ids, *args):
        number = self.pool.get('ir.sequence').get(cr, uid, 'sale.order')
        self.write(cr, uid, ids, {'name':number})
        super(SaleOrder, self).action_wait(cr, uid, ids, *args)
        
    def copy(self, cr, uid, id, default=None,context={}):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'shipped':False,
            'invoice_ids':[],
            'picking_ids':[],
            'name': 'SO/',
        })
        return super(SaleOrder, self).copy(cr, uid, id, default, context)
SaleOrder()
