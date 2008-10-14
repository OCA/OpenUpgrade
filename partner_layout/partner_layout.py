# -*- encoding: utf-8 -*-
import time

from osv import fields
from osv import osv


class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'header' : fields.binary('Header (.odt)'),
        'logo' : fields.binary('Logo'),
        'signature' : fields.binary('Signature')
    }
    
    def _default_company(self, cr, uid, context={}):
        if 'category_id' in context and context['category_id']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category_id'])])[0]
            return [id_cat]
        return []
   
    _defaults = {
        'category_id': _default_company,
    }
res_partner()
