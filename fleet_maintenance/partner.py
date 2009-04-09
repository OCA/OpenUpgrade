from osv import fields,osv

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    _columns = {
        'fleets': fields.one2many('stock.location', 'partner_id', 'Fleets'),
        'sub_fleets': fields.one2many('stock.location', 'parent_partner_id', 'Sub Fleets'),
     }
res_partner()