# -*- encoding: utf-8 -*-
import time

from osv import fields
from osv import osv


class partner_layout(osv.osv):
    _name = "partner.layout"
    _columns = {
        'header' : fields.binary('Header (.odt)'),
        'logo' : fields.binary('Logo'),
        'signature' : fields.binary('Signature')
    }
    
partner_layout()