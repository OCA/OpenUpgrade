from osv import fields,osv
import tools
import ir
import pooler


class sale_order_line(osv.osv):
    _inherit = "sale.order.line" 
    
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Fleet'),
        'maintainance_start_date':fields.date('Maintenance Start Date', required = False),
        'maintainance_end_date':fields.date('Maintenance End Date', required = False),
    }
    
    #FIXME deal with invoice on delivery
    def invoice_line_create(self, cr, uid, ids, context={}):
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        print create_ids
        i=0
        for line in self.browse(cr, uid, ids, context):
            self.pool.get('account.invoice.line').write(cr,uid,[create_ids[i]],{'maintainance_start_date':line.maintainance_start_date})
            self.pool.get('account.invoice.line').write(cr,uid,[create_ids[i]],{'maintainance_end_date':line.maintainance_end_date})
            self.pool.get('account.invoice.line').write(cr,uid,[create_ids[i]],{'fleet_id':line.fleet_id.id})
            i=i+1
        return create_ids
    

sale_order_line()