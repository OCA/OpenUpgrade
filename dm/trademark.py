# -*- encoding: utf-8 -*-
import time

from osv import fields
from osv import osv


class dm_trademark(osv.osv):
    _name = "dm.trademark"
    _inherit = "res.partner"
    _columns = {
        'partner_layout':fields.many2one('partner.layout','Layout')
    }
dm_trademark()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

