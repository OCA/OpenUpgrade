from osv import fields,osv
import tools
import ir
import pooler

class crm_case(osv.osv):
    _inherit = "crm.case" 
    _columns = {
        'fleet_id': fields.many2one('stock.location', 'Fleet', required = False, select = True),
        'picking_id': fields.many2one('stock.picking', 'Repair Movement', required = False, select = True),
    }
crm_case()