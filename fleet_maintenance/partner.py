from osv import fields,osv
import tools
import ir
import pooler

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'fleets': fields.one2many('stock.location', 'partner_id', 'Fleets'),
    }
res_partner()