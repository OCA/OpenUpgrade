from osv import fields,osv
import tools
import ir
import pooler

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _name = "account.invoice.line" 
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Fleet'),
        'maintainance_start_date':fields.date('Maintenance Start Date', required = False),
        'maintainance_end_date':fields.date('Maintenance End Date', required = False),
    }
        
account_invoice_line()