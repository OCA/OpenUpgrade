from osv import fields, osv
from osv import orm
class res_partner(osv.osv):
    _inherit = 'res.partner'

    def create(self, cr, uid, vals, *args, **kwargs):
        list_lang = []
        ids_lang = self.pool.get('res.lang').search(cr, uid, [])
        lang = self.pool.get('res.lang').browse(cr, uid, ids_lang)
        for l in lang:
            list_lang.append(l.code)
        d= {}
        if 'lang' in vals and not vals['lang'] in list_lang:
            d['lang']=''
            vals.update(d)
        return super(res_partner,self).create(cr, uid, vals, *args, **kwargs)

res_partner()
