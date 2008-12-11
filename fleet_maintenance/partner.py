from osv import fields,osv
import tools
import ir
import pooler

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def _get_sub_fleets(self, cr, uid, ids, *args):
        res = {}
        for partner in self.browse(cr, uid, ids):
            for fleet in partner.fleets:
                tab = []
                for sub_fleet in fleet.child_ids:
                    tab.append(sub_fleet.id)
                res[partner.id] = tab
        return res
    
    _columns = {
        'fleets': fields.one2many('stock.location', 'partner_id', 'Fleets'),
        #'sub_fleets': fields.one2many(_get_sub_fleets, method = True, type = 'one2many', relation = 'stock.location', string="Sub Fleets"),
    }
res_partner()