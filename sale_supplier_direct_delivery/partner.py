from osv import fields, osv

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    
    def _complete_name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        table = self.name_get(cr, uid, ids, {'contact_display':'contact'})
        return dict(table)
    
    _columns = {
        'complete_address': fields.function(_complete_name_get_fnc, method=True, type="char", size=512, string='Complete Name'),
    }
    
res_partner_address()