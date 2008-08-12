# -*- encoding: utf-8 -*-
import time

from osv import fields
from osv import osv


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = "res.partner"
    _columns = {
        'partner_layout_id':fields.many2one('partner.layout','Layout')
    }
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:












