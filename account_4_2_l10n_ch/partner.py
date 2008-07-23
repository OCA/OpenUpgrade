# -*- encoding: utf-8 -*-
from osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'ref_companies': fields.one2many('res.company', 'partner_id',
        'Companies that refers to partner'),
    }

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

