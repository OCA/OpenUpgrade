from osv import fields,osv
import tools
import ir
import pooler

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _name = "account.invoice.line" 
    _columns = {
        'maintenance_month_qty': fields.float('Maintenance Month Quantity', required=False),
        'maintenance_product_qty': fields.float('Maintenance Product Quantity', required=False), 
        'fleet_id': fields.many2one('stock.location', 'Fleet'),
        'maintenance_start_date':fields.date('Maintenance Start Date', required = False),
        'maintenance_end_date':fields.date('Maintenance End Date', required = False),
        'is_maintenance': fields.related('product_id', 'is_maintenance', type='boolean', string='Is Maintenance'),
    }
        
account_invoice_line()