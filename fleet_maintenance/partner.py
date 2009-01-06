from osv import fields,osv
import tools
import ir
import pooler

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def _get_sub_fleets(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            tab = []
            for fleet in partner.fleets:
                tab.append(fleet.id)
                for sub_fleet in fleet.child_ids:
                    tab.append(sub_fleet.id)
            res[partner.id] = tab
        return res
    
    _columns = {
        'fleets': fields.one2many('stock.location', 'partner_id', 'Fleets'),
        'sub_fleets': fields.function(_get_sub_fleets, method = True, type = 'one2many', relation = 'stock.location', string="Sub Fleets"),
     }
res_partner()