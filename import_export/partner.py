# -*- encoding: utf-8 -*-

from osv import fields, osv
import ir

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'
    
    _columns = {
        'partner_location': fields.selection([('local','Local Partner'),('europe','Europe Partner'),('outside','Worldwild Partner')],'Partner Location'),
    }
#end class
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

