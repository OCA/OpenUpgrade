# -*- encoding: utf-8 -*-
import time

from osv import fields
from osv import osv


class dm_trademark(osv.osv):
    _name = "dm.trademark"
    _inherit = "res.partner"
    _columns = {
        'header' : fields.binary('Header (.odt)'),
        'logo' : fields.binary('Logo'),
        'signature' : fields.binary('Signature')
    }
    
dm_trademark()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

