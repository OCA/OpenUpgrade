# -*- encoding: utf-8 -*-
import time

from osv import fields
from osv import osv


class dm_trademark(osv.osv):
    _name = "dm.trademark"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=6, required=True),
        'partner_id' : fields.many2one('res.partner', 'Partner', required=False),
        'header' : fields.binary('Header (.odt)'),
        'logo' : fields.binary('Logo'),
        'signature' : fields.binary('Signature')
    }

dm_trademark()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

