from osv import osv, fields
import pooler


def _lang_get(self, cr, uid, context={}):
    obj = self.pool.get('res.lang')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['code', 'name'], context)
    res = [(r['code'], r['name']) for r in res]
    return res + [(False, '')]

class ecommerce_partner(osv.osv):
    _description='Partner Ecommerce'
    _name = "ecommerce.partner"
    _order = "name"
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'contact_name': fields.char('Contact Name', size=128, required=True, select=True),
        'lang': fields.selection(_lang_get, 'Language', size=5),
        'username':fields.char('User Name',size=128,select=True),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('E-Mail', size=64),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),
        'active': fields.boolean('Active'),
        'category_ids': fields.many2many('res.partner.category', 'ecommerce_partner_category_rel', 'partner_id', 'category_id', 'Categories'),
       
    }
    _defaults = {
        'active': lambda *a: 1,
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the partner must be unique !')
    ]

    def copy(self, cr, uid, id, default=None, context={}):
        name = self.read(cr, uid, [id], ['name'])[0]['name']
        default.update({'name': name+' (copy)'})
        return super(res_partner, self).copy(cr, uid, id, default, context)
    
       
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

ecommerce_partner()

