from osv import fields,osv

class res_partner(osv.osv):
    _inherit = 'res.partner' 
    _columns = {
        'magento_id': fields.integer('Magento partner id'),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
    }
res_partner()